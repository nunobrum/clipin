"""
Cross-platform clipboard manager without external dependencies
"""

import platform
import subprocess
import sys


class Clipboard:
    """A simple clipboard manager that works across different platforms"""
    
    def __init__(self):
        self.system = platform.system()
        
    def copy(self, text):
        """Copy text to clipboard
        
        Args:
            text: String to copy to clipboard
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not isinstance(text, str):
            text = str(text)
            
        try:
            if self.system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
                
            elif self.system == "Windows":
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                process.communicate(text.encode('utf-16le'))
                return process.returncode == 0
                
            elif self.system == "Linux":
                # Try xclip first
                try:
                    process = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    process.communicate(text.encode('utf-8'))
                    if process.returncode == 0:
                        return True
                except FileNotFoundError:
                    pass
                
                # Try xsel as fallback
                try:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    process.communicate(text.encode('utf-8'))
                    return process.returncode == 0
                except FileNotFoundError:
                    raise RuntimeError(
                        "No clipboard utility found. Please install xclip or xsel: "
                        "sudo apt-get install xclip"
                    )
            else:
                raise RuntimeError(f"Unsupported operating system: {self.system}")
                
        except Exception as e:
            print(f"Error copying to clipboard: {e}", file=sys.stderr)
            return False
    
    def paste(self):
        """Get text from clipboard
        
        Returns:
            str: Text from clipboard, or empty string if unsuccessful
        """
        try:
            if self.system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['pbpaste'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                return output.decode('utf-8')
                
            elif self.system == "Windows":
                process = subprocess.Popen(
                    ['powershell', '-command', 'Get-Clipboard'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                output, _ = process.communicate()
                return output.decode('utf-16le', errors='ignore').strip()
                
            elif self.system == "Linux":
                # Try xclip first
                try:
                    process = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard', '-o'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    output, _ = process.communicate()
                    if process.returncode == 0:
                        return output.decode('utf-8')
                except FileNotFoundError:
                    pass
                
                # Try xsel as fallback
                try:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--output'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    output, _ = process.communicate()
                    return output.decode('utf-8')
                except FileNotFoundError:
                    raise RuntimeError(
                        "No clipboard utility found. Please install xclip or xsel: "
                        "sudo apt-get install xclip"
                    )
            else:
                raise RuntimeError(f"Unsupported operating system: {self.system}")
                
        except Exception as e:
            print(f"Error pasting from clipboard: {e}", file=sys.stderr)
            return ""
    
    def clear(self):
        """Clear the clipboard
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.copy("")


# Convenience module-level functions
_default_clipboard = None


def _get_clipboard():
    """Get or create the default clipboard instance"""
    global _default_clipboard
    if _default_clipboard is None:
        _default_clipboard = Clipboard()
    return _default_clipboard


def copy(text):
    """Copy text to clipboard
    
    Args:
        text: String to copy to clipboard
        
    Returns:
        bool: True if successful, False otherwise
    """
    return _get_clipboard().copy(text)


def paste():
    """Get text from clipboard
    
    Returns:
        str: Text from clipboard, or empty string if unsuccessful
    """
    return _get_clipboard().paste()


def clear():
    """Clear the clipboard
    
    Returns:
        bool: True if successful, False otherwise
    """
    return _get_clipboard().clear()
