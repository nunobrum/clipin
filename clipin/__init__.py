"""
clipin - A simple python clipboard manager without dependencies
"""

from .clipboard import Clipboard, ClipboardError, copy, paste, clear, available_formats

__version__ = "0.1.0"
__all__ = ["Clipboard", "ClipboardError", "copy", "paste", "clear", "available_formats"]
