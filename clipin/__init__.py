import sys
import subprocess
import ctypes
import time
from typing import Union, Optional, Dict, List


class ClipboardError(Exception):
    pass

types_to_stringify = (str, int, float, bool)

def _stringify_text(text):
    if not isinstance(text, types_to_stringify):
        raise ClipboardError(
            'only str, int, float, and bool values can be copied to the clipboard, not %s' % text.__class__.__name__)
    return str(text)


if sys.platform.startswith("win"):
    from ctypes import c_size_t, sizeof, c_wchar_p, get_errno, c_wchar, windll, string_at
    from ctypes.wintypes import (HGLOBAL, LPVOID, DWORD, LPCSTR, INT, HWND,
                                 HINSTANCE, HMENU, BOOL, UINT, HANDLE, CHAR)
    try:
        from PIL import Image
    except ImportError:
        _use_pil = False
    else:
        _use_pil = True
        import io
        # Use relative import to avoid ModuleNotFoundError when package is imported
        from .win_dib import convert_dib_to_image, convert_image_to_dib_bytes
        from .win_dib import parse_dib_to_png as _parse_dib_to_png  # used in tests

    msvcrt = ctypes.CDLL('msvcrt')

    import contextlib

    GMEM_MOVEABLE = 0x0002

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
    TEXT_FORMATS_NEEDING_ENCODING = (CF_TEXT, CF_DSPTEXT)

    # --- Base Mappings ---
    MIME_CF_MAPPINGS = (
        # Text formats
        ("text/plain", CF_TEXT),
        ("text/html", CF_UNICODETEXT),  # Using CF_UNICODETEXT for html encodings. This needs to come first for the mapping to work
        ("text/plain;charset=utf-16", CF_UNICODETEXT),
        ("text/plain;charset=oem", CF_OEMTEXT),
        ("text/locale", CF_LOCALE),

        # Image formats
        ("image/x-win-bmp", CF_BITMAP),  # This is not working for paste operations
        ("image/x-win-dib", CF_DIB),
        ("image/x-win-dibv5", CF_DIBV5),
        ("image/tiff", CF_TIFF),
        ("image/x-wmf", CF_METAFILEPICT),
        ("image/x-emf", CF_ENHMETAFILE),

        # Audio formats
        ("audio/x-wav", CF_WAVE),
        ("audio/x-riff", CF_RIFF),

        # Data / spreadsheet formats
        ("application/vnd.ms-sylk", CF_SYLK),
        ("application/x-dif", CF_DIF),
        ("application/x-ms-pen", CF_PENDATA),

        # File / drag-and-drop
        ("application/x-file-list", CF_HDROP),

        # Palette / graphics
        ("application/x-color-palette", CF_PALETTE),

        # Display / owner / private
        ("application/x-owner-display", CF_OWNERDISPLAY),
        ("application/x-display-text", CF_DSPTEXT),
        ("application/x-display-bitmap", CF_DSPBITMAP),
        ("application/x-display-metafile", CF_DSPMETAFILEPICT),
        ("application/x-display-enhmetafile", CF_DSPENHMETAFILE),

        # Private / GDI ranges
        # ("application/x-private-format", CF_PRIVATEFIRST, CF_PRIVATELAST),
        # ("application/x-gdi-object", CF_GDIOBJFIRST, CF_GDIOBJLAST),
    )

    NATIVE_IMAGES_MIME_TYPES = list(item[0] for item in MIME_CF_MAPPINGS if item[0].startswith('image/'))

    # --- Derived Dictionaries ---
    def mime_to_cf(mimep) -> int:
        for mime, cf in MIME_CF_MAPPINGS:
            if mime == mimep:
                return cf
        for cf, desc in STANDARD_FORMAT_DESCRIPTION.items():
            if desc == mimep:
                return cf
        raise ClipboardError(f"MIME {mimep} has no corresponding CF Format")

    def cf_to_mime(cfp):
        if cfp not in STANDARD_FORMAT_DESCRIPTION:
            raise ClipboardError(f"CF Code {cfp} not supported")
        for mime, cf in MIME_CF_MAPPINGS:
            if cf == cfp:
                return mime
        return STANDARD_FORMAT_DESCRIPTION[cfp]

    def _try_mime(cf_or_mime):
        try:
            cf_or_mime = cf_to_mime(cf_or_mime)
        except ClipboardError:
            pass
        return cf_or_mime

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


    def copy(data: Union[dict, str, bytes], clip_format: Union[str, int] = CF_UNICODETEXT):
        """
        Copies the provided data to the Windows clipboard in the specified clipboard format.
        It makes use of Windows API functions to manage the clipboard.
        The data parameter can also be a dictionary is provided, it can copy multiple formats in one
        operation.  The function ensures to acquire a valid window handle and clipboard
        ownership before performing the operation.

        For multiplatform compatibility, this function is made to accept the POSIX MIME types.
        The mapping between the MIME Types and CF Formats is the given in the CF_MIME_MAPPINGS tuple list.

        :param data: The text or dictionary to be copied to the clipboard. If a
            dictionary is provided, each key-value pair represents a clipboard format
            and its corresponding text content.
        :type data: str or dict
        :param clip_format: The clipboard format for the provided text. It defaults to
            CF_UNICODETEXT. If a string is provided, it will be converted to the
            appropriate clipboard format using a predefined mapping.
        :type clip_format: int or str
        :return: None
        :rtype: None
        :raises ValueError: If invalid data or format is provided or an error occurs
            during the clipboard operation.
        """
        # This function is heavily based on
        # http://msdn.com/ms649016#_win32_Copying_Information_to_the_Clipboard

        if isinstance(data, dict):
            # Transform all MIME types to CF codes
            text_dict = {cf: cf_data for cf, cf_data in data.items()}
        else:
            text_dict = {clip_format: data}

        with window() as hwnd:
            # http://msdn.com/ms649048
            # If an application calls OpenClipboard with hwnd set to NULL,
            # EmptyClipboard sets the clipboard owner to NULL;
            # this causes SetClipboardData to fail.
            # => We need a valid hwnd to copy something.
            with clipboard(hwnd):
                safeEmptyClipboard()

                for clip_format, clip_data in text_dict.items():
                    # Treat the MIME types that are not supported in Windows
                    # image/png, image/jpeg, image/gif, etc.
                    if isinstance(clip_format, str):
                        if clip_format.startswith('image/') and clip_format not in NATIVE_IMAGES_MIME_TYPES:
                            if _use_pil is False:
                                raise ClipboardError(f"PIL library not found. Cannot copy image format {clip_format}.\n"
                                                     f"Install Pillow using the command: pip install pillow")
                            clip_data = convert_image_to_dib_bytes(image_data=clip_data, dib_format=CF_DIB)
                            clip_format = CF_DIB
                        else:
                            clip_format = mime_to_cf(clip_format)
                    elif clip_format in (CF_DIB, CF_DIBV5):
                        if (clip_data.startswith(b'BM')  # BMP signature
                            or clip_data.startswith(b'\x89PNG')  # PNG signature
                            or clip_data.startswith(b'\x49\x49')  # TIFF signature
                            or clip_data.startswith(b'\x4D\x4D')  # TIFF signature
                            or clip_data.startswith(b'\xFF\xD8\xFF')):  # JPEG signature
                            if _use_pil is False:
                                raise ClipboardError(f"PIL library not found. Cannot copy DIB format {clip_format}.\n"
                                                 f"Install Pillow using the command: pip install pillow")
                            clip_data = convert_image_to_dib_bytes(image_data=clip_data, dib_format=clip_format)
                        else:
                            # Assert that clip_data is already in DIB format
                            assert isinstance(clip_data, bytes), "DIB data must be bytes"
                            # Read header size (first 4 bytes, little endian)
                            header_size = int.from_bytes(clip_data[0:4], 'little')
                            if header_size not in (12, 40, 108, 124):
                                raise ClipboardError("DIB data has invalid header size")

                    assert isinstance(clip_format, int), "clip_format must be an int at this point"

                    if isinstance(clip_data, types_to_stringify):
                        clip_data = _stringify_text(clip_data)  # Converts non-str values to str.
                        if clip_format in TEXT_FORMATS_NEEDING_ENCODING:
                            clip_data = clip_data.encode('utf-8')

                    if clip_data:
                        # http://msdn.com/ms649051
                        # If the hMem parameter identifies a memory object,
                        # the object must have been allocated using the
                        # function with the GMEM_MOVEABLE flag.
                        if isinstance(clip_data, bytes):  # This passes in an 8 bit format.
                            count = len(clip_data) + 1
                            handle = safeGlobalAlloc(GMEM_MOVEABLE,
                                                     count * sizeof(CHAR))
                            locked_handle = safeGlobalLock(handle)
                            ctypes.memmove(LPCSTR(locked_handle), LPCSTR(clip_data), count * sizeof(CHAR))

                            safeGlobalUnlock(handle)
                            safeSetClipboardData(clip_format, handle)
                        else:
                            count = wcslen(clip_data) + 1
                            handle = safeGlobalAlloc(GMEM_MOVEABLE,
                                                     count * sizeof(c_wchar))
                            locked_handle = safeGlobalLock(handle)
                            ctypes.memmove(c_wchar_p(locked_handle), c_wchar_p(clip_data), count * sizeof(c_wchar))

                            safeGlobalUnlock(handle)
                            safeSetClipboardData(clip_format, handle)


    def paste(clip_format: Union[str, int] = None, use_mime=True) -> Union[str, bytes, Dict[str, Union[str, bytes]]]:
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
            For compatibility, if a MIME Type is passed, an equivalent MIME Type will be used.

        :param use_mime: If True, the function will attempt to use MIME types for clipboard
            format negotiation. This is useful for applications that need to work with
            web content or other environments where MIME types are the standard.

        :return: If a single format is provided, returns the data for that format,
            decoded accordingly based on the format type. If multiple formats are
            provided, return a dictionary where the keys are format types and the
            values are the respective data retrieved. In case of failure or empty
            clipboard data for any specific format, the value will be None.
        :rtype: Union[str, dict[str, Union[str, bytes]]]
        """
        answer = {}
        preferred_image_format = None  # used when converting DIB to image format
        if clip_format is None or clip_format == 0 or (
                isinstance(clip_format, (list, tuple)) and len(clip_format) == 0):
            # Will retrieve the list of available formats
            clip_formats = available_formats(use_mime=False)
            single_output = False
        elif isinstance(clip_format, (list, tuple)):
            clip_formats = clip_format
            single_output = False
        else:
            clip_formats = (clip_format,)  # Use provided format as a list
            single_output = True

        with clipboard(None):

            for clip_format in clip_formats:
                # Transform MIME types to CF codes
                if isinstance(clip_format, str):
                    if clip_format.startswith('image/') and clip_format not in NATIVE_IMAGES_MIME_TYPES:
                        # Treat the MIME types that are not supported in Windows
                        # image/png, image/jpeg, image/gif, etc.
                        preferred_image_format = clip_format[6:].upper() # exclude 'image/' prefix
                        cf = CF_DIB  # We will try to get DIB format to convert later
                    else:
                        cf = mime_to_cf(clip_format)
                else:
                    cf = clip_format

                assert isinstance(cf, int), "clip_format must be an int at this point, it's %s" % type(cf)
                if cf == CF_BITMAP:
                    continue  # Bitmap format not supported for retrieval. TODO: Investigate later

                handle = safeGetClipboardData(cf)
                if handle:
                    try:
                        if cf == CF_UNICODETEXT:
                            data = c_wchar_p(handle).value
                        else:
                            size = safeGlobalSize(handle)
                            data = string_at(safeGlobalLock(handle), size)
                            safeGlobalUnlock(handle)
                    except:
                        answer[clip_format] = None
                        continue
                    # Decode text formats
                    if cf in TEXT_FORMATS_NEEDING_ENCODING:
                        data = data.decode('utf-8')

                    if (cf == CF_DIB or cf == CF_DIBV5) and \
                            preferred_image_format is not None:
                        if _use_pil:
                            # Windows DIB format includes a BITMAPINFOHEADER structure at the start
                            # and data is encoded differently.
                            # If PIL exists, it can be used to parse the data
                            # and convert it to a PNG or BMP format.
                            img = convert_dib_to_image(data)
                            if img is None:
                                answer[clip_format] = data  # keep original DIB data if conversion fails
                                continue
                            output = io.BytesIO()
                            img.save(output, format=preferred_image_format)
                            data = output.getvalue()
                        else:
                            print("PIL library not found. Cannot convert DIB to image format.\n"
                                  "Install Pillow using the command: pip install pillow")
                        preferred_image_format = None # only convert or print warning once
                    answer[clip_format] = data

        # now will see if only one is returned or the complete list
        if single_output:
            return answer[clip_format]
        else:
            # if it is a list, check whether to use MIME types
            if use_mime:
                return {_try_mime(cfp): data for cfp, data in answer.items()}
            else:
                return answer


    def available_formats(use_mime=True) -> List[Union[str, int]]:
        formats = []
        with clipboard(None):
            fmt = 0
            while True:
                fmt = safeEnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                if use_mime:
                    formats.append(_try_mime(fmt))
                else:
                    formats.append(fmt)
            return formats


elif sys.platform == "darwin":
    import logging

    try:
        import AppKit
        from AppKit import NSPasteboard
        from Foundation import NSData
    except ImportError:
        _use_appkit = False
        NF_MIME_MAPPINGS = {}
    else:
        _use_appkit = True
        NF_MIME_MAPPINGS = {
            'text/plain': 'NSPasteboardTypeString',
            'text/html': 'NSPasteboardTypeHTML',
            'text/rtf': 'NSPasteboardTypeRTF',
            'image/png': 'NSPasteboardTypePNG',
            'image/tiff': 'NSPasteboardTypeTIFF',
        }
        APPLE_MIME_MAPPINGS = {
            'public.utf8-plain-text': 'text/plain',
        }

        TEXT_FORMATS_NEEDING_ENCODING = {
            'public.utf8-plain-text': 'utf-8',
            'NSStringPboardType': 'utf-8',
            'public.utf16-external-plain-text': 'utf-16'

        }


    def display_warning(clip_format):
        if not _use_appkit and clip_format != 'text/plain':
            print("MIME clipboard support on macOS requires additional libraries.\n" \
                  "Install PyObjC + Cocoa using the command: pip install pyobjc\n"
                  "use 'text/plain' as clip_format to avoid this message.")


    # macOS implementation.
    def paste(clip_format: Union[str, list[str], tuple[str]] = None):
        """
        Gets the contents of the clipboard. If there are more than one clipboard format, it returns the
        :param clip_format:
        :return:
        """
        result = {}
        if _use_appkit:
            if clip_format is None or clip_format == 0 or clip_format == '' or (
                isinstance(clip_format, (list, tuple)) and len(clip_format) == 0):
                # Will retrieve the list of available formats
                clip_formats = "*/*"
                single_output = False
            elif isinstance(clip_format, (list, tuple)):
                clip_formats = clip_format
                single_output = False
            else:
                clip_formats = (clip_format,)  # Use provided format as a list
                single_output = True

            pb = NSPasteboard.generalPasteboard()

            for pb_type in pb.types():
                data = pb.dataForType_(pb_type)
                if data is not None:
                    # Tries to convert if possible
                    data = bytes(data)
                    if pb_type in TEXT_FORMATS_NEEDING_ENCODING:
                        coding = TEXT_FORMATS_NEEDING_ENCODING[pb_type]
                        data = data.decode(coding)
                    mime_type = APPLE_MIME_MAPPINGS.get(pb_type, pb_type)
                    if clip_formats == "*/*" or mime_type in clip_formats or pb_type in clip_formats:
                        result[mime_type] = data

        else:
            display_warning(clip_format)
            try:
                result['text/plain'] = subprocess.check_output(['pbpaste'], text=True)
            except Exception as e:
                raise ClipboardError(f"Failed to get clipboard data: {e}")
            single_output = clip_format == 'text/plain'

        if single_output and clip_format in result:
            result = result[clip_format]

        return result


    def copy(data, clip_format: str = None):
        """
        Copies the provided data to the MAC OSX clipboard in the specified clipboard format.
        If PyObjC library is installed, it allows the user to set one or more clipboard formats.
        If PyObjC is not found it will try to use pbcopy tool instead, but in this case, only
        plain UTF-8 compatible strings are allowed.

        With pbcopy, data must be a str type. With PyObjC data type depends on the clip format
        being used.

        These are the predefined MIME formats in Mac OSX (Monterey):

        NSPasteboardTypeColor: com.apple.cocoa.pasteboard.color
        NSPasteboardTypeFileURL: public.file-url
        NSPasteboardTypeFindPanelSearchOptions: com.apple.cocoa.pasteboard.find-panel-search-options
        NSPasteboardTypeFont: com.apple.cocoa.pasteboard.character-formatting
        NSPasteboardTypeHTML: public.html
        NSPasteboardTypeMultipleTextSelection: com.apple.cocoa.pasteboard.multiple-text-selection
        NSPasteboardTypePDF: com.adobe.pdf
        NSPasteboardTypePNG: public.png
        NSPasteboardTypeRTF: public.rtf
        NSPasteboardTypeRTFD: com.apple.flat-rtfd
        NSPasteboardTypeRuler: com.apple.cocoa.pasteboard.paragraph-formatting
        NSPasteboardTypeSound: com.apple.cocoa.pasteboard.sound
        NSPasteboardTypeString: public.utf8-plain-text
        NSPasteboardTypeTIFF: public.tiff
        NSPasteboardTypeTabularText: public.utf8-tab-separated-values-text
        NSPasteboardTypeTextFinderOptions: com.apple.cocoa.pasteboard.find-panel-search-options
        NSPasteboardTypeURL: public.url

        For an updated list issue the following commands:
        >>> import AppKit
        >>> >>> print('\n'.join(f"{a}: getattr(AppKit,a)" for a in dir(AppKit) if a.startswith('NSPasteboardType')))


        Multiple data formats can be set at the same time. In this case data should be
        a dictionary, where the keys represent the

        """
        if _use_appkit:
            pb = NSPasteboard.generalPasteboard()
            pb.clearContents()

            if not isinstance(data, dict):

                if clip_format is None or len(clip_format)==0:
                    clip_format = 'text/plain'

                data = {clip_format: data}


            copies_done = []
            for paste_type, data in data.items():
                # Need to convert to apple's recognized types
                cf_type = NF_MIME_MAPPINGS.get(paste_type, paste_type)
                if cf_type.startswith("NSPasteboardType"):
                    cf_type = getattr(AppKit, cf_type)
                if isinstance(data, types_to_stringify):
                    data = _stringify_text(data)  # Converts non-str values to str.
                if cf_type in TEXT_FORMATS_NEEDING_ENCODING and isinstance(data, str):
                    coding = TEXT_FORMATS_NEEDING_ENCODING[cf_type]
                    data = data.encode(coding)
                nsdata = NSData.dataWithBytes_length_(data, len(data))
                pb.setData_forType_(nsdata, cf_type)
                copies_done.append(cf_type)

            # now verify if copy was successful
            verify_copy = False
            if verify_copy:
                for pb_type in pb.types():
                    if pb_type in copies_done:
                        del copies_done[copies_done.index(pb_type)]
                if len(copies_done) > 0:
                    raise ClipboardError(f"Unable to copy these formats: {copies_done}")

        else:
            display_warning(clip_format)

            if clip_format is None or len(clip_format)==0:
                clip_format = 'text/plain'
    
            if clip_format == 'text/plain':
                if isinstance(data, str):
                    data = data.encode('utf-8')
                elif not isinstance(data, bytes):
                    raise ClipboardError("For text formats data shall be str or bytes")

                p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                p.communicate(input=data)
            else:
                raise ClipboardError(f"MIME type not supported : '{clip_format}'")


    def available_formats() -> list[str]:
        clipboard_contents:dict = paste(None)
        return list(clipboard_contents.keys())


elif sys.platform.startswith("linux"):
    # Linux implementation
    def is_text_format(clip_format: str) -> bool:
        return clip_format is None or clip_format.startswith('text')

    def print_xclip_missing_warning():
        print("xclip not found. Please install xclip to use advanced clipboard features.\n"
              "To install xclip in Debian/Ubuntu-based distributions :\n"
              "   > sudo apt update\n"
              "   > sudo apt install xclip\n"
              "For Fedora/RHEL-based systems:\n"
              "   > sudo dnf install xclip\n"
              "For Arch-based systems:\n"
              "   > sudo pacman -S xclip\n"
              )

    def paste(clip_format: Optional[str] = None) -> Union[dict, bytes, str]:
        result = {}
        if clip_format:
            clip_formats = clip_format if isinstance(clip_format, (set, list, tuple)) else (clip_format, )
        else:
            clip_formats = available_formats()

        for cf in clip_formats:
            try:
                result[cf] = subprocess.check_output(
                    ['xclip', '-selection', 'clipboard', '-t', cf, '-out'], text=is_text_format(cf))

            except FileNotFoundError:
                print_xclip_missing_warning()
                if 'text/html' in clip_format:
                    import tkinter as tk
                    r = tk.Tk()
                    r.withdraw()  # Hide the main window
                    return {'text/html' : r.clipboard_get()}
            except Exception:
                pass

        if not clip_format:
            return result
        else:
            if clip_format in result:
                return result[clip_format]
            else:
                raise ClipboardError(f"{clip_format} not in clipboard. Available formats are  {result.keys()}")


    def copy(data, clip_format: str = None):
        if clip_format is None:
            # Will try to determine a type
            if isinstance(data, types_to_stringify):
                data = _stringify_text(data)  # Converts non-str values to str.
                clip_format = 'text/plain'
            elif isinstance(data, dict):
                if len(data) == 0:
                    raise ClipboardError(f"If dict is passed, it should contain at least one element.")
                else:
                    print_warning =  len(data) > 1
                    clip_format, data = next(iter(data.items()))
                    if print_warning:
                        print(f"Sorry! Multiple formats not supported in Linux.")
            else:
                try:
                    data.decode('utf-8')  # if it decodes, it is text
                except UnicodeDecodeError:
                    # try to find some clues from the data being passed
                    # if it starts with PNG header bytes
                    if data.startswith(b'\x89PNG\r\n\x1a\n'):
                        clip_format = 'image/png'
                    # JPEG header bytes
                    elif data.startswith(b'\xff\xd8\xff'):
                        clip_format = 'image/jpeg'
                    # GIF header bytes
                    elif data.startswith(b'GIF8'):
                        clip_format = 'image/gif'
                else:
                    clip_format = 'text/plain'

        if is_text_format(clip_format):
            data = data.encode('utf-8') if isinstance(data, str) else data
        try:
            p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', clip_format], stdin=subprocess.PIPE)
            p.communicate(input=data)
        except FileNotFoundError:
            print_xclip_missing_warning()
            if is_text_format(clip_format):
                import tkinter as tk
                r = tk.Tk()
                r.withdraw()  # Hide the main window
                r.clipboard_clear()
                r.clipboard_append(data.decode('utf-8'))
                r.update()  # Keep data even after script exits
        except Exception as e:
            raise ClipboardError(f"Failed to set clipboard data: {e}")

    def available_formats() -> list[str]:
        try:
            formats = subprocess.check_output(['xclip', '-selection', 'clipboard', '-t', 'TARGETS', '-out'], text=True)
            formats = formats.splitlines()
        except FileNotFoundError:
            formats = ['text/plain']
        except Exception:
            formats = []
        return formats
