# clipin
A simple python clipboard manager without dependencies

## Features

- Cross-platform support (Windows, macOS, Linux)
- No external Python dependencies
- Simple and intuitive API
- Lightweight and fast

## Installation

```bash
pip install clipin
```

Or install from source:

```bash
git clone https://github.com/nunobrum/clipin.git
cd clipin
pip install .
```

## Usage

### Basic Usage

```python
from clipin import copy, paste, clear

# Copy text to clipboard
copy("Hello, World!")

# Get text from clipboard
text = paste()
print(text)  # Output: Hello, World!

# Clear clipboard
clear()
```

### Using the Clipboard Class

```python
from clipin import Clipboard

clipboard = Clipboard()

# Copy text
clipboard.copy("Some text")

# Paste text
text = clipboard.paste()

# Clear clipboard
clipboard.clear()
```

## Platform Requirements

- **Windows**: Built-in clipboard support (no additional requirements)
- **macOS**: Built-in `pbcopy` and `pbpaste` commands (no additional requirements)
- **Linux**: Requires `xclip` or `xsel` to be installed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install xclip
  
  # Or alternatively
  sudo apt-get install xsel
  ```

## API Reference

### Functions

- `copy(text)` - Copy text to clipboard. Returns `True` on success.
- `paste()` - Get text from clipboard. Returns the clipboard content as a string.
- `clear()` - Clear the clipboard. Returns `True` on success.

### Clipboard Class

- `Clipboard()` - Create a new clipboard manager instance
- `clipboard.copy(text)` - Copy text to clipboard
- `clipboard.paste()` - Get text from clipboard
- `clipboard.clear()` - Clear the clipboard

## License

MIT License - see LICENSE file for details
