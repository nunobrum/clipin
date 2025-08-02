import sys
import subprocess
import ctypes
import os
import platform
from ctypes import wintypes


class ClipboardError(Exception):
    pass


class ClipBeast:
    @staticmethod
    def get(formats=None):
        if sys.platform.startswith("win"):
            return ClipBeast._get_windows(formats)
        elif sys.platform == "darwin":
            return ClipBeast._get_macos()
        elif sys.platform.startswith("linux"):
            return ClipBeast._get_linux()
        else:
            raise ClipboardError("Unsupported platform")

    @staticmethod
    def set(data: bytes, format_name: str = 'text/plain'):
        if sys.platform.startswith("win"):
            ClipBeast._set_windows(data, format_name)
        elif sys.platform == "darwin":
            ClipBeast._set_macos(data, format_name)
        elif sys.platform.startswith("linux"):
            ClipBeast._set_linux(data, format_name)
        else:
            raise ClipboardError("Unsupported platform")

    @staticmethod
    def available_formats():
        if sys.platform.startswith("win"):
            return ClipBeast._available_formats_windows()
        elif sys.platform == "darwin":
            return ['text/plain', 'text/html', 'image/png']
        elif sys.platform.startswith("linux"):
            return ['text/plain', 'text/html', 'image/png']
        else:
            return []

    # Windows implementation
    @staticmethod
    def _get_windows(formats=None):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        if not user32.OpenClipboard(0):
            raise ClipboardError("Failed to open clipboard")

        result = {}
        fmt = 0
        while True:
            fmt = user32.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            if formats is not None and fmt not in formats:
                continue
            handle = user32.GetClipboardData(fmt)
            if handle:
                ptr = kernel32.GlobalLock(handle)
                size = kernel32.GlobalSize(handle)
                buffer = ctypes.create_string_buffer(size)
                ctypes.memmove(buffer, ptr, size)
                result[fmt] = buffer.raw
                kernel32.GlobalUnlock(handle)

        user32.CloseClipboard()
        return result

    @staticmethod
    def _set_windows(data: bytes, format_name: str):
        GMEM_MOVEABLE = 0x0002

        format_map = {
            'text/plain': 13,
            'text/ascii': 1,
            'image/bmp': 8,
            'text/html': 49322,
        }
        fmt = format_map.get(format_name)

        if fmt is None:
            fmt = ctypes.windll.user32.RegisterClipboardFormatW(format_name)

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        if not user32.OpenClipboard(0):
            raise ClipboardError("Failed to open clipboard")
        user32.EmptyClipboard()

        h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h_global:
            user32.CloseClipboard()
            raise ClipboardError("Failed to allocate global memory")

        locked_mem = kernel32.GlobalLock(h_global)
        ctypes.memmove(locked_mem, data, len(data))
        kernel32.GlobalUnlock(h_global)

        if not user32.SetClipboardData(fmt, h_global):
            user32.CloseClipboard()
            raise ClipboardError("Failed to set clipboard data")

        user32.CloseClipboard()

    @staticmethod
    def _available_formats_windows():
        user32 = ctypes.windll.user32

        if not user32.OpenClipboard(0):
            raise ClipboardError("Failed to open clipboard")

        formats = []
        fmt = 0
        while True:
            fmt = user32.EnumClipboardFormats(fmt)
            if fmt == 0:
                break
            formats.append(fmt)

        user32.CloseClipboard()
        return formats

    # macOS implementation
    @staticmethod
    def _get_macos():
        try:
            result = {'text/plain': subprocess.check_output(['pbpaste'], text=True)}
            try:
                html = subprocess.check_output([
                    'osascript', '-e', 'the clipboard as "HTML"'
                ], stderr=subprocess.DEVNULL)
                result['text/html'] = html.decode(errors='ignore')
            except:
                pass
            try:
                png_data = subprocess.check_output(['osascript', '-e', 'get the clipboard as "PNGf"'], stderr=subprocess.DEVNULL)
                result['image/png'] = png_data
            except:
                result['image/png'] = b''
            return result
        except Exception as e:
            raise ClipboardError(f"Failed to get clipboard data: {e}")

    @staticmethod
    def _set_macos(data: bytes, format_name: str):
        try:
            if format_name == 'text/plain':
                p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                p.communicate(input=data)
            elif format_name == 'text/html':
                p = subprocess.Popen(['osascript', '-e', f'set the clipboard to {{{data.decode("utf-8")} as «class HTML»}}'], stdin=subprocess.PIPE)
                p.communicate()
            elif format_name == 'image/png':
                raise ClipboardError("Image clipboard support on macOS requires additional tools or custom scripting.")
            else:
                raise ClipboardError("Unsupported format for macOS")
        except Exception as e:
            raise ClipboardError(f"Failed to set clipboard data: {e}")

    # Linux implementation
    @staticmethod
    def _get_linux():
        try:
            result = {'text/plain': subprocess.check_output(['xclip', '-selection', 'clipboard', '-out'], text=True)}
            try:
                html = subprocess.check_output(['xclip', '-selection', 'clipboard', '-t', 'text/html', '-out'], text=True)
                result['text/html'] = html
            except:
                pass
            try:
                png = subprocess.check_output(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-out'])
                result['image/png'] = png
            except:
                result['image/png'] = b''
            return result
        except FileNotFoundError:
            raise ClipboardError("xclip not found. Please install xclip to use advanced clipboard features.")
        except Exception as e:
            raise ClipboardError(f"Failed to get clipboard data: {e}")

    @staticmethod
    def _set_linux(data: bytes, format_name: str):
        try:
            if format_name == 'text/plain':
                p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            elif format_name == 'text/html':
                p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'text/html'], stdin=subprocess.PIPE)
            elif format_name == 'image/png':
                p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/png'], stdin=subprocess.PIPE)
            else:
                raise ClipboardError("Unsupported format for Linux")
            p.communicate(input=data)
        except FileNotFoundError:
            raise ClipboardError("xclip not found. Please install xclip to use advanced clipboard features.")
        except Exception as e:
            raise ClipboardError(f"Failed to set clipboard data: {e}")
