# 🧠 clipin

**clipin** is a pure-Python, <s>cross-platform</s> windows (for the time being) clipboard utility that supports multiple clipboard formats—text, HTML, 
and images (where supported)—without third-party dependencies.

## ✅ Features

- ✅ Cross-platform: Windows, MacOS, Linux
- 🧩 Supports MIME formats (1):
  - `text/plain`
  - `text/html`
  - `image/tiff`

(1) requires xclip in linux and pyobjc in MacOS. If these are not present, it will support only 
basic text copy and paste.

Windows doesn't have a MIME like clipboard identifiers and MacOX have different MIME strings than Linux.
The library makes internally a mapping between MIMEs as per the following table. However, the user can use 
as well the OS identifiers, in this case losing code compatibility.

Here is a non-exhaustive list of the mappings done:

| Linux      | Windows (2)         | MacOSX - darwin (3)                             |
|------------|---------------------|-------------------------------------------------|
| text/plain | CF_TEXT = 1         | NSPasteboardTypeString = public.utf8-plain-text |
| text/html  | CF_UNICODETEXT = 13 | NSPasteboardTypeHTML = public.html              |
| image/bmp  | CF_BITMAP = 2       | No equivalent (5)                               |
| image/png  | No equivalent (4)   | NSPasteboardTypePNG = public.png                |
| image/tiff | CF_TIFF = 6         | NSPasteboardTypeTIFF = public.tiff              |

(2) Windows uses integer numbers to represent different clipboard formats

(3) MacOSX defines in the AppKit library the strings for the most commonly used formats

(4) Either use the CF_DIB or CF_DIBV5 for Windows compressed bitmaps<br>
    Windows places more information on the clipboard, additional manipulation may be needed.<br>
    See https://docs.microsoft.com/en-us/windows/win32/dataxchg/standard-clipboard-formats for more details.

(5) MacOSX does not have a native bitmap format, use PNG or TIFF instead

## 🚀 Installation

```bash
pip install clipin
```
## 📦 Usage

```python
import clipin as cb
cb.copy("Hello, World!")
print(cb.paste())  # Outputs: Hello, World!
```

Copying an image file to the clipboard.
```python
import clipin
png_filename = "image_file.png"
with open(png_filename) as f:
   clipin.copy(f.readall(), 'image/png')
```

Copying both filename and image
```python
import clipin
png_filename = "image_file.png"
with open(png_filename) as f:
   clipin.copy({'image/png': f.readall(), 'text/plain': png_filename})
```
