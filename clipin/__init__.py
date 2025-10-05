"""
clipin - A simple python clipboard manager without dependencies
"""

from .clipboard import Clipboard, copy, paste, clear

__version__ = "0.1.0"
__all__ = ["Clipboard", "copy", "paste", "clear"]
