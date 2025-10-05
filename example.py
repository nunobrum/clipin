"""
Example usage of clipin clipboard manager
"""

from clipin import copy, paste, clear

# Example 1: Copy text to clipboard
text_to_copy = "Hello from clipin!"
if copy(text_to_copy):
    print(f"Successfully copied: {text_to_copy}")
else:
    print("Failed to copy to clipboard")

# Example 2: Paste text from clipboard
pasted_text = paste()
print(f"Clipboard contains: {pasted_text}")

# Example 3: Using the Clipboard class directly
from clipin import Clipboard

clipboard = Clipboard()
clipboard.copy("Another example text")
print(f"From class: {clipboard.paste()}")

# Example 4: Clear the clipboard
if clear():
    print("Clipboard cleared")
    print(f"Clipboard after clear: '{paste()}'")
