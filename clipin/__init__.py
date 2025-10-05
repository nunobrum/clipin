import sys
import subprocess
import ctypes
import time


class ClipboardError(Exception):
    pass


PY2 = sys.version_info[0] == 2


def _stringify_text(text):
    acceptedTypes = (str, int, float, bool)
    if not isinstance(text, acceptedTypes):
        raise ClipboardError(
            'only str, int, float, and bool values can be copied to the clipboard, not %s' % text.__class__.__name__)
    return str(text)


if sys.platform.startswith("win"):
    from ctypes import c_size_t, sizeof, c_wchar_p, get_errno, c_wchar, windll, string_at
    from ctypes.wintypes import (HGLOBAL, LPVOID, DWORD, LPCSTR, INT, HWND,
                                 HINSTANCE, HMENU, BOOL, UINT, HANDLE, CHAR)

    msvcrt = ctypes.CDLL('msvcrt')

    import contextlib

    GMEM_MOVEABLE = 0x0002

    ENCODING = 'utf-8'

    # Windows-related clipboard functions:
    class CheckedCall(object):
        def __init__(self, f):
            super(CheckedCall, self).__setattr__("f", f)

        def __call__(self, *args):
            ret = self.f(*args)
            if not ret and get_errno():
                raise ClipboardError("Error calling " + self.f.__name__)
            return ret

        def __setattr__(self, key, value):
            setattr(self.f, key, value)

    # Standard Clipboard Formats in Windows
    # Constant = value          # Description
    CF_BITMAP = 2  # A handle to a bitmap (HBITMAP).
    CF_DIB = 8  # A memory object containing a BITMAPINFO structure followed by the bitmap bits.
    CF_DIBV5 = 17  # A memory object containing a BITMAPV5HEADER structure followed by the bitmap color
    # space information and the bitmap bits.
    CF_DIF = 5  # Software Arts' Data Interchange Format.
    CF_DSPBITMAP = 0x0082  # Bitmap display format associated with a private format. The hMem parameter must be a
    # handle to data that can be displayed in bitmap format in lieu of the privately
    # formatted data.
    CF_DSPENHMETAFILE = 0x008E  # Enhanced metafile display format associated with a private format.
    # The hMem parameter must be a handle to data that can be displayed in enhanced metafile
    # format in lieu of the privately formatted data.
    CF_DSPMETAFILEPICT = 0x0083  # Metafile-picture display format associated with a private format. The hMem parameter
    # must be a handle to data that can be displayed in metafile-picture format in lieu of
    # the privately formatted data.
    CF_DSPTEXT = 0x0081  # Text display format associated with a private format. The hMem parameter must be a
    # handle to data that can be displayed in text format in lieu of the privately formatted
    # data.
    CF_ENHMETAFILE = 14  # A handle to an enhanced metafile (HENHMETAFILE).
    CF_GDIOBJFIRST = 0x0300  # Start of a range of integer values for application-defined GDI object clipboard
    # formats. The end of the range is CF_GDIOBJLAST.
    # Handles associated with clipboard formats in this range are not automatically deleted
    # using the GlobalFree function when the clipboard is emptied. Also, when using values
    # in this range, the hMem parameter is not a handle to a GDI object, but is a handle
    # allocated by the GlobalAlloc function with the GMEM_MOVEABLE flag.
    CF_GDIOBJLAST = 0x03FF  # See CF_GDIOBJFIRST.
    CF_HDROP = 15  # A handle to type HDROP that identifies a list of files. An application can retrieve
    # information about the files by passing the handle to the DragQueryFile function.
    CF_LOCALE = 16  # The data is a handle to the locale identifier associated with text in the clipboard.
    # When you close the clipboard, if it contains CF_TEXT data but no CF_LOCALE data, the
    # system automatically sets the CF_LOCALE format to the current input language. You can
    # use the CF_LOCALE format to associate a different locale with the clipboard text.
    # An application that pastes text from the clipboard can retrieve this format to
    # determine which character set was used to generate the text.
    # Note that the clipboard does not support plain text in multiple character sets.
    # To achieve this, use a formatted text data type such as RTF instead.
    # The system uses the code page associated with CF_LOCALE to implicitly convert from
    # CF_TEXT to CF_UNICODETEXT. Therefore, the correct code page table is used for the
    # conversion.
    CF_METAFILEPICT = 3  # Handle to a metafile picture format as defined by the METAFILEPICT structure. When
    # passing a CF_METAFILEPICT handle by means of DDE, the application responsible for
    # deleting hMem should also free the metafile referred to by the CF_METAFILEPICT handle.
    CF_OEMTEXT = 7  # Text format containing characters in the OEM character set. Each line ends with a
    # carriage return/linefeed (CR-LF) combination. A null character signals the end of the
    # data.
    CF_OWNERDISPLAY = 0x0080  # Owner-display format. The clipboard owner must display and update the clipboard viewer
    # window, and receive the WM_ASKCBFORMATNAME, WM_HSCROLLCLIPBOARD, WM_PAINTCLIPBOARD,
    # WM_SIZECLIPBOARD, and WM_VSCROLLCLIPBOARD messages. The hMem parameter must be NULL.
    CF_PALETTE = 9  # Handle to a color palette. Whenever an application places data in the clipboard that
    # depends on or assumes a color palette, it should place the palette on the clipboard as
    # well.
    # If the clipboard contains data in the CF_PALETTE (logical color palette) format, the
    # application should use the SelectPalette and RealizePalette functions to realize
    # (compare) any other data in the clipboard against that logical palette.
    # When displaying clipboard data, the clipboard always uses as its current palette any
    # object on the clipboard that is in the CF_PALETTE format.
    CF_PENDATA = 10  # Data for the pen extensions to the Microsoft Windows for Pen Computing.
    CF_PRIVATEFIRST = 0x0200  # Start of a range of integer values for private clipboard formats. The range ends with
    # CF_PRIVATELAST. Handles associated with private clipboard formats are not freed
    # automatically; the clipboard owner must free such handles, typically in response to
    # the WM_DESTROYCLIPBOARD message.
    CF_PRIVATELAST = 0x02FF  # See CF_PRIVATEFIRST.
    CF_RIFF = 11  # Represents audio data more complex than can be represented in a CF_WAVE standard wave
    # format.
    CF_SYLK = 4  # Microsoft Symbolic Link (SYLK) format.
    CF_TEXT = 1  # Text format. Each line ends with a carriage return/linefeed (CR-LF) combination.
    # A null character signals the end of the data. Use this format for ANSI text.
    CF_TIFF = 6  # Tagged-image file format.
    CF_UNICODETEXT = 13  # Unicode text format. Each line ends with a carriage return/linefeed (CR-LF)
    # combination. A null character signals the end of the data.
    CF_WAVE = 12  # Represents audio data in one of the standard wave formats, such as 11 kHz or
    # 22 kHz PCM.

    CF_ALL = []  # If passing an iterable to the paste function, it will retrieve all available formats

    STANDARD_FORMAT_DESCRIPTION = {
        # Identifier: "Descriptor",
        CF_BITMAP: "BITMAP",
        CF_DIB: "DIB",
        CF_DIBV5: "DIBV5",
        CF_DIF: "DIF",
        CF_DSPBITMAP: "DSP BITMAP",
        CF_DSPENHMETAFILE: "DSP ENHMETAFILE",
        CF_DSPMETAFILEPICT: "DSP METAFILEPICT",
        CF_DSPTEXT: "DSP TEXT",
        CF_ENHMETAFILE: "ENHMETAFILE",
        CF_GDIOBJFIRST: "GDIOBJ FIRST",
        CF_GDIOBJLAST: "GDIOBJ LAST",
        CF_HDROP: "Handle Drag and DROP",
        CF_LOCALE: "LOCALE",
        CF_METAFILEPICT: "METAFILE PICT",
        CF_OEMTEXT: "OEM TEXT",
        CF_OWNERDISPLAY: "OWNER DISPLAY",
        CF_PALETTE: "PALETTE",
        CF_PENDATA: "Microsoft PEN DATA",
        CF_PRIVATEFIRST: "PRIVATE FIRST",
        CF_PRIVATELAST: "PRIVATE LAST",
        CF_RIFF: "RIFF",
        CF_SYLK: "SYLK",
        CF_TEXT: "TEXT",
        CF_TIFF: "TIFF",
        CF_UNICODETEXT: "UNICODE TEXT",
        CF_WAVE: "WAVE",
    }
    TEXT_FORMATS_NEEDING_ENCONDING = (CF_TEXT, CF_DSPTEXT)

    MIME_TO_CF = {
        # --- Text formats ---
        "text/plain": CF_TEXT,  # ANSI text
        "text/plain;charset=unicode": CF_UNICODETEXT,  # UTF-16 (Windows native)
        "text/plain;charset=oem": CF_OEMTEXT,  # OEM character set text
        "text/locale": CF_LOCALE,  # Locale information (metadata)

        # --- Image / bitmap formats ---
        "image/bmp": CF_BITMAP,  # Native HBITMAP handle
        "image/x-dib": CF_DIB,  # Device Independent Bitmap
        "image/vnd.ms-photo": CF_DIBV5,  # BITMAPV5HEADER (high color depth)
        "image/tiff": CF_TIFF,  # Tagged Image File Format
        "image/x-wmf": CF_METAFILEPICT,  # Windows Metafile
        "image/x-emf": CF_ENHMETAFILE,  # Enhanced Metafile

        # --- Audio / multimedia ---
        "audio/vnd.wave": CF_WAVE,  # Standard WAV audio
        "audio/x-wav": CF_WAVE,  # Alias for wave audio
        "audio/x-riff": CF_RIFF,  # RIFF audio container

        # --- Spreadsheet / data formats ---
        "application/vnd.ms-sylk": CF_SYLK,  # Microsoft Symbolic Link
        "application/x-dif": CF_DIF,  # Data Interchange Format
        "application/x-ms-pen": CF_PENDATA,  # Pen computing data

        # --- File drops (drag & drop) ---
        "application/x-msdownload": CF_HDROP,  # File drop list
        "application/x-file-list": CF_HDROP,  # Common alias

        # --- Palette / graphics ---
        "application/x-color-palette": CF_PALETTE,  # Logical color palette

        # --- Owner / display / private formats ---
        "application/x-owner-display": CF_OWNERDISPLAY,
        "application/x-display-text": CF_DSPTEXT,
        "application/x-display-bitmap": CF_DSPBITMAP,
        "application/x-display-metafile": CF_DSPMETAFILEPICT,
        "application/x-display-enhmetafile": CF_DSPENHMETAFILE,

        # --- Private / GDI / system-defined ---
        # "application/x-private-format": CF_PRIVATEFIRST–CF_PRIVATELAST,
        # "application/x-gdi-object": CF_GDIOBJFIRST–CF_GDIOBJLAST,
    }

    safeCreateWindowExA = CheckedCall(windll.user32.CreateWindowExA)
    safeCreateWindowExA.argtypes = [DWORD, LPCSTR, LPCSTR, DWORD, INT, INT,
                                    INT, INT, HWND, HMENU, HINSTANCE, LPVOID]
    safeCreateWindowExA.restype = HWND

    safeDestroyWindow = CheckedCall(windll.user32.DestroyWindow)
    safeDestroyWindow.argtypes = [HWND]
    safeDestroyWindow.restype = BOOL

    OpenClipboard = windll.user32.OpenClipboard
    OpenClipboard.argtypes = [HWND]
    OpenClipboard.restype = BOOL

    safeCloseClipboard = CheckedCall(windll.user32.CloseClipboard)
    safeCloseClipboard.argtypes = []
    safeCloseClipboard.restype = BOOL

    safeEnumClipboardFormats = CheckedCall(windll.user32.EnumClipboardFormats)
    safeEnumClipboardFormats.argtypes = [INT]
    safeEnumClipboardFormats.restype = UINT

    safeGetClipboardFormatName = CheckedCall(windll.user32.GetClipboardFormatNameW)
    safeGetClipboardFormatName.argtypes = [INT, LPCSTR]
    safeGetClipboardFormatName.restype = UINT

    safeEmptyClipboard = CheckedCall(windll.user32.EmptyClipboard)
    safeEmptyClipboard.argtypes = []
    safeEmptyClipboard.restype = BOOL

    safeGetClipboardData = CheckedCall(windll.user32.GetClipboardData)
    safeGetClipboardData.argtypes = [UINT]
    safeGetClipboardData.restype = HANDLE

    safeSetClipboardData = CheckedCall(windll.user32.SetClipboardData)
    safeSetClipboardData.argtypes = [UINT, HANDLE]
    safeSetClipboardData.restype = HANDLE

    safeGlobalAlloc = CheckedCall(windll.kernel32.GlobalAlloc)
    safeGlobalAlloc.argtypes = [UINT, c_size_t]
    safeGlobalAlloc.restype = HGLOBAL

    safeGlobalLock = CheckedCall(windll.kernel32.GlobalLock)
    safeGlobalLock.argtypes = [HGLOBAL]
    safeGlobalLock.restype = LPVOID

    safeGlobalUnlock = CheckedCall(windll.kernel32.GlobalUnlock)
    safeGlobalUnlock.argtypes = [HGLOBAL]
    safeGlobalUnlock.restype = BOOL

    safeGlobalSize = CheckedCall(windll.kernel32.GlobalSize)
    safeGlobalSize.argtypes = [HGLOBAL]
    safeGlobalSize.restyoe = UINT

    wcslen = CheckedCall(msvcrt.wcslen)
    wcslen.argtypes = [c_wchar_p]
    wcslen.restype = UINT

    # Windows implementation
    @contextlib.contextmanager
    def window():
        """
        Context that provides a valid Windows hwnd.
        """
        # we really just need the hwnd, so setting "STATIC"
        # as predefined lpClass is just fine.
        hwnd = safeCreateWindowExA(0, b"STATIC", None, 0, 0, 0, 0, 0,
                                   None, None, None, None)
        try:
            yield hwnd
        finally:
            safeDestroyWindow(hwnd)

    @contextlib.contextmanager
    def clipboard(hwnd):
        """
        Context manager that opens the clipboard and prevents
        other applications from modifying the clipboard content.
        """
        # We may not get the clipboard handle immediately because
        # some other application is accessing it (?)
        # We try for at least 500ms to get the clipboard.
        t = time.time() + 0.5
        success = False
        while time.time() < t:
            success = OpenClipboard(hwnd)
            if success:
                break
            time.sleep(0.01)
        if not success:
            raise ClipboardError("Error calling OpenClipboard")

        try:
            yield
        finally:
            safeCloseClipboard()


    def copy(text_or_dict, clip_format=CF_UNICODETEXT):
        # This function is heavily based on
        # http://msdn.com/ms649016#_win32_Copying_Information_to_the_Clipboard

        if isinstance(text_or_dict, dict):
            text_dict = text_or_dict
        else:
            text_dict = {clip_format: text_or_dict}

        with window() as hwnd:
            # http://msdn.com/ms649048
            # If an application calls OpenClipboard with hwnd set to NULL,
            # EmptyClipboard sets the clipboard owner to NULL;
            # this causes SetClipboardData to fail.
            # => We need a valid hwnd to copy something.
            with clipboard(hwnd):
                safeEmptyClipboard()

                for clip_format, text in text_dict.items():
                    if (not PY2) and (not isinstance(text, bytes)):
                        text = _stringify_text(text)  # Converts non-str values to str.
                        if clip_format in TEXT_FORMATS_NEEDING_ENCONDING:
                            text = text.encode(ENCODING)

                    if text:
                        # http://msdn.com/ms649051
                        # If the hMem parameter identifies a memory object,
                        # the object must have been allocated using the
                        # function with the GMEM_MOVEABLE flag.
                        if (not PY2) and isinstance(text, bytes):  # This passes in an 8 bit format.
                            count = len(text) + 1
                            handle = safeGlobalAlloc(GMEM_MOVEABLE,
                                                     count * sizeof(CHAR))
                            locked_handle = safeGlobalLock(handle)
                            ctypes.memmove(LPCSTR(locked_handle), LPCSTR(text), count * sizeof(CHAR))

                            safeGlobalUnlock(handle)
                            safeSetClipboardData(clip_format, handle)
                        else:
                            count = wcslen(text) + 1
                            handle = safeGlobalAlloc(GMEM_MOVEABLE,
                                                     count * sizeof(c_wchar))
                            locked_handle = safeGlobalLock(handle)
                            ctypes.memmove(c_wchar_p(locked_handle), c_wchar_p(text), count * sizeof(c_wchar))

                            safeGlobalUnlock(handle)
                            safeSetClipboardData(clip_format, handle)


    def paste(clip_format=CF_UNICODETEXT) -> str | dict[str, str|bytes]:
        """
        Retrieve data from the clipboard for a specific format or multiple formats.

        This function interacts with the clipboard to retrieve data stored in specific
        formats. It supports both single and multiple formats. If multiple formats are
        provided, the function aggregates data from all specified formats into a
        dictionary where keys are format identifiers and values are the corresponding
        data retrieved.

        :param clip_format: The clipboard format to retrieve. This can be one of the
            predefined clipboard formats like CF_UNICODETEXT, or a list/tuple of
            formats for multi-format retrieval. Defaults to CF_UNICODETEXT.

        :return: If a single format is provided, returns the data for that format,
            decoded accordingly based on the format type. If multiple formats are
            provided, returns a dictionary where the keys are format types and the
            values are the respective data retrieved. In case of failure or empty
            clipboard data for any specific format, the value will be None.
        :rtype: Union[str, dict[str, Union[str, bytes]]]
        """
        answer = {}
        if clip_format is None or clip_format == 0 or (
                isinstance(clip_format, (list, tuple)) and len(clip_format) == 0):
            # Will retrieve the list of available formats
            clip_formats = available_formats()
            single_output = False
        elif isinstance(clip_format, (list, tuple)):
            clip_formats = clip_format
            single_output = False
        else:
            clip_formats = (clip_format,)  # Use provided format as a list
            single_output = True

        with clipboard(None):

            for clip_format in clip_formats:
                handle = safeGetClipboardData(clip_format)
                if not handle:
                    answer[clip_format] = None
                else:
                    if clip_format == CF_UNICODETEXT:
                        text = c_wchar_p(handle).value
                    else:
                        size = safeGlobalSize(handle)
                        text = string_at(safeGlobalLock(handle), size)
                        safeGlobalUnlock(handle)
                        if clip_format in TEXT_FORMATS_NEEDING_ENCONDING:
                            text.decode(ENCODING)
                    answer[clip_format] = text

            # now will see if only one is returned or the complete list
        return answer[clip_format] if single_output else answer


    def available_formats():
        formats = []
        with clipboard(None):
            fmt = 0
            while True:
                fmt = safeEnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                formats.append(fmt)
            return formats


elif sys.platform == "darwin":

    # macOS implementation
    def paste():
        try:
            result = {'text/plain': subprocess.check_output(['pbpaste'], text=True)}
            try:
                html = subprocess.check_output([
                    'osascript', '-e', 'the clipboard as "HTML"'
                ], stderr=subprocess.DEVNULL)
                result['text/html'] = html.decode(errors='ignore')
            except Exception:
                pass
            try:
                png_data = subprocess.check_output(['osascript', '-e', 'get the clipboard as "PNGf"'],
                                                   stderr=subprocess.DEVNULL)
                result['image/png'] = png_data
            except Exception:
                result['image/png'] = b''
            return result
        except Exception as e:
            raise ClipboardError(f"Failed to get clipboard data: {e}")


    def copy(data: bytes, format_name: str):
        try:
            if format_name == 'text/plain':
                p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                p.communicate(input=data)
            elif format_name == 'text/html':
                p = subprocess.Popen(
                    ['osascript', '-e', f'set the clipboard to {{{data.decode("utf-8")} as «class HTML»}}'],
                    stdin=subprocess.PIPE)
                p.communicate()
            elif format_name == 'image/png':
                raise ClipboardError(
                    "Image clipboard support on macOS requires additional tools or custom scripting.")
            else:
                raise ClipboardError("Unsupported format for macOS")
        except Exception as e:
            raise ClipboardError(f"Failed to set clipboard data: {e}")


elif sys.platform.startswith("linux"):
    # Linux implementation

    def paste():
        try:
            result = {'text/plain': subprocess.check_output(['xclip', '-selection', 'clipboard', '-out'], text=True)}
            try:
                html = subprocess.check_output(['xclip', '-selection', 'clipboard', '-t', 'text/html', '-out'],
                                               text=True)
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


    def copy(data: bytes, format_name: str):
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
