# 🧠 clipin

**clipin** is a pure-Python, cross-platform clipboard utility that supports multiple clipboard formats—text, HTML, 
and images (where supported) with minimal third-party dependencies.

## ✅ Features

- ✅ Cross-platform: Windows, macOS, Linux
- 🧩 Supports formats:
  - `text/plain`
  - `text/html`
  - `image/png`
- ❌ No third-party Python packages (degraded mode)

## 🚀 Installation

```bash
pip install clipin
```
## 📦 Usage

```python
import clipin

clipin.copy("Hello, World!")
print(clipin.paste('text/plain'))  # Outputs: Hello, World!

