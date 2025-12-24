# 🧠 clipin

**clipin** is a pure-Python clipboard utility that supports multiple clipboard formats — text, HTML, and images (where supported) — with minimal third-party dependencies.

## ✅ Features

- ✅ Cross-platform: Windows, macOS, Linux
- 🧩 Supports MIME formats[^1]:
  - `text/plain`
  - `text/html`
  - `image/png ; image/bmp ; image/tiff` (where supported)
- 🔄 Copy and paste multiple formats at once (where supported)
- 🐍 Pure Python with minimal dependencies

[^1]: Requires `xclip` on Linux and `pyobjc` on macOS. If these are not present, clipin will support only basic text copy and paste.

Windows doesn't use MIME-style clipboard identifiers, and macOS uses different MIME strings than Linux. The library internally maps common MIME types to platform-specific clipboard identifiers; you can also use OS-specific identifiers directly, but that may reduce cross-platform compatibility.

Here is a non-exhaustive list of the mappings performed:

| Linux      | Windows[^2]         | macOS (Darwin)[^3]                              |
|------------|---------------------|-------------------------------------------------|
| text/plain | CF_TEXT = 1         | NSPasteboardTypeString = public.utf8-plain-text |
| text/html  | CF_UNICODETEXT = 13 | NSPasteboardTypeHTML = public.html              |
| image/bmp  | CF_BITMAP = 2       | No equivalent[^5]                               |
| image/png  | No equivalent[^4]   | NSPasteboardTypePNG = public.png                |
| image/tiff | CF_TIFF = 6         | NSPasteboardTypeTIFF = public.tiff              |

[^2]: Windows represents many clipboard formats as integer constants.

[^3]: macOS exposes common pasteboard types via AppKit (NSPasteboard / NSPasteboard.PasteboardType).

[^4]: On Windows, images are typically stored on the clipboard as CF_DIB / CF_DIBV5 (Device Independent Bitmaps) rather than as PNG or JPEG files. clipin will:

    - Detect native Windows bitmap formats
    - Convert them to PNG if the Pillow library is available

    If Pillow is not installed, clipin exposes the raw bitmap data and documents how to enable PNG conversion.

    To enable PNG conversion, install Pillow:

    ```bash
    pip install pillow
    ```

    See: https://docs.microsoft.com/en-us/windows/win32/dataxchg/standard-clipboard-formats

[^5]: macOS does not have a native Windows-style bitmap format; prefer PNG or TIFF.

## 🚀 Installation

```bash
pip install clipin
```

## 📦 Usage

Copy and paste simple text:

```python
import clipin as cb
cb.copy("Hello, World!")
print(cb.paste())  # Outputs: Hello, World!
```

Copy an image file to the clipboard (open files in binary mode):

```python
import clipin
filename = "image_file.tiff"
with open(filename, "rb") as f:
    clipin.copy(f.read(), "image/tiff")
```

Copy both a filename and image data (not supported on all platforms):

```python
import clipin
filename = "image_file.png"
with open(filename, "rb") as f:
    clipin.copy({"image/png": f.read(), "text/plain": filename})
```
