import sys
import unittest
from clipbeast import ClipBeast, ClipboardError


class TestClipBeast(unittest.TestCase):

    def test_text_plain_roundtrip(self):
        text = "Hello from ClipBeast!"
        ClipBeast.set(text.encode('utf-8'), 'text/plain')
        data = ClipBeast.get().get('text/plain')
        self.assertIn("Hello", data)

    def test_available_formats_returns_list(self):
        formats = ClipBeast.available_formats()
        self.assertIsInstance(formats, list)

    def test_set_invalid_format(self):
        with self.assertRaises(ClipboardError):
            ClipBeast.set(b'unsupported data', 'application/unknown')

    def test_get_returns_dict(self):
        result = ClipBeast.get()
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
