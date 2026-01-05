# 🧠 clipin

**clipin** is a pure-Python clipboard utility that supports multiple clipboard formats — text, HTML, and images (where supported) — with minimal third-party dependencies.

## ✅ Features

- ✅ Cross-platform: Windows, macOS, Linux. However, headless systems (without a display), like bare bones containers, are not supported.
- 🧩 Supports MIME formats[^1] (where supported, see table below):
  - `text/plain`
  - `text/html`
  - `image/png ; image/bmp ; image/tiff`
- 🔄 Copy and paste multiple formats at once (where supported)
- 🐍 Pure Python with minimal dependencies (Python 3.9+)

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

See the capabilities of the clipboard on the current platform:

```python
import clipin
caps = clipin.capabilities()
print(caps)
# Example output on Windows:
# {'textplain': True, 'mime': True, 'multiple_formats_copy': True, 'multiple_formats_paste': True}
```

See table below.

## 📚 Interacting with MIME Types across Platforms

clipin uses MIME types (e.g., `text/plain`, `image/png`) to identify clipboard data formats. This approach enhances cross-platform compatibility, as different operating systems have their own clipboard format identifiers.
However, note that Windows doesn't use MIME-style clipboard identifiers, so clipin maps between MIME types and Windows clipboard formats internally. To do this, clipin uses the Pillow library for image format conversions when necessary.

Here is a non-exhaustive list of the mappings performed:

| Linux      | Windows[^2]         | macOS (Darwin)[^3]                              |
|------------|---------------------|-------------------------------------------------|
| text/plain | CF_TEXT = 1         | NSPasteboardTypeString = public.utf8-plain-text |
| text/html  | CF_UNICODETEXT = 13 | NSPasteboardTypeHTML = public.html              |
| image/bmp  | CF_BITMAP = 2 [^4]  | No equivalent[^5]                               |
| image/png  | No equivalent[^6]   | NSPasteboardTypePNG = public.png                |
| image/tiff | CF_TIFF = 6         | NSPasteboardTypeTIFF = public.tiff              |
| image/jpeg | No equivalent[^6]   | NSPasteboardTypeJPEG = public.jpeg              |
| image/gif  | No equivalent[^6]   | NSPasteboardTypeGIF = com.compuserve.gif        |

## Recommended Libraries

clipin is designed to be lightweight, with minimal dependencies. However, for enhanced functionality, especially regarding image format conversions on Windows, the following optional libraries are recommended:

- Windows: [Pillow](https://pypi.org/project/Pillow/) (for image format conversions)
- Linux: [xclip](https://opensource.com/article/19/7/xclip) (command line tool for clipboard access)
- macOS: [pyobjc](https://pypi.org/project/pyobjc/) (for advanced clipboard interactions)

Without these libraries, clipin will still function for basic text copy and paste operations. The table below summarizes the capabilities based on the presence of these optional libraries.

| Condition                     | textplain:<br>text/plain | mime:<br>text/html<br>image/* | multiple_formats_copy | multiple_formats_paste |
|-------------------------------|:---------:|:------:|:---------------------:|:----------------------:|
| Windows                       | ✅        | ✅     | ✅                    | ✅                     |
| MacOS with pyobjc             | ✅        | ✅     | ✅                    | ✅                     |
| MacOS, no pyobjc              | ✅        | ❌     | ❌                    | ❌                     |
| Linux with xclip              | ✅        | ✅     | ❌                    | ✅                     |
| Linux, with tkinter, no xclip | ✅        | ❌     | ❌                    | ❌                     |
| Linux, no tkinter nor xclip   | ❌        | ❌     | ❌                    | ❌                     |
| Linux, headless               | ❌        | ❌     | ❌                    | ❌                     |

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements and Credits

This project was inspired on [pyperclip](https://github.com/asweigart/pyperclip), a library that almost everyone used and loved, but unfortunately was stalled.
Firstly the pull-requests where not being attended and support for the new wheel package format was not being added.
The initial goal of this project was to fork pyperclip and continue its development, but the scope quickly expanded.

The development of this library followed 4 basic principles:
1. Keep it simple to use. No object-oriented API, just simple functions to copy and paste.
2. Maintain cross-platform compatibility.
3. Support multiple clipboard formats.
4. Minimal dependencies. If third-party libraries are needed, they should be optional and only for enhanced functionality.

This project development was aided by ChatGPT-4 and GitHub Copilot. 
The long discussions on possibilities and implementation options were very helpful to clarify the design decisions.
Also the implementation of DIB handling on Windows and NSPasteboard interactions on macOS were greatly simplified by the suggestions of these AI tools.
Special thanks to the open-source community for creating and maintaining tools like pyperclip, Pillow, xclip, and pyobjc, which made this project possible.

Finally thanks to my wife and kids for their patience while I was working on this project.

I hope you find clipin useful! 😊
Stay well and happy coding! 🚀

## ⚙️ Notes

[^1]: Requires `xclip` on Linux and `pyobjc` on macOS. If these are not present, clipin will need python-tk installed to support only text copy and paste. If you run in a headless system, like bare bones linux container images, clipin will not work, unless you set up a virtual display (e.g., using Xvfb).

[^2]: Windows represents many clipboard formats as integer constants.

[^3]: macOS exposes common pasteboard types via AppKit (NSPasteboard / NSPasteboard.PasteboardType).

[^4]: On Windows, CF_BITMAP represents a device-dependent bitmap format. clipin is not exploiting this format directly; instead, it focuses on CF_DIB / CF_DIBV5 for image clipboard operations.

[^5]: macOS does not have a native Windows-style bitmap format; prefer PNG or TIFF.

[^6]: On Windows, images are typically stored on the clipboard as CF_DIB / CF_DIBV5 (Device Independent Bitmaps) rather than as PNG or JPEG files. clipin will:

    - Detect native Windows bitmap formats
    - Convert them to PNG if the Pillow library is available

    If Pillow is not installed, clipin exposes the raw bitmap data and documents how to enable PNG conversion.

    To enable PNG conversion, install Pillow:

    ```bash
    pip install pillow
    ```

    See: https://docs.microsoft.com/en-us/windows/win32/dataxchg/standard-clipboard-formats

