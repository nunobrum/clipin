
import unittest
import clipin

from clipin import ClipboardError


class TestClipin(unittest.TestCase):

    def test_text_plain_roundtrip(self):
        text = "Hello from clipin!"
        clipin.copy(text)
        data = clipin.paste()
        self.assertIn("Hello", data)

    def test_available_formats_returns_list(self):
        formats = clipin.available_formats()
        self.assertIsInstance(formats, list)
        print("Available Formats are : ", formats)

    def test_set_invalid_format(self):
        with self.assertRaises(ClipboardError):
            clipin.copy(b'unsupported data', 'application/unknown')

        # clipin.copy(b'unsupported data', 'text/plain')
        # with self.assertRaises(ClipboardError):
        #     clipin.paste('text/plain')

    def test_get_returns_dict(self):
        clipin.copy("Sample Text")
        result = clipin.paste()
        self.assertIsInstance(result, str)

        result = clipin.paste('text/plain')
        self.assertIsInstance(result, str)

        result = clipin.paste([])
        self.assertIsInstance(result, dict)


        print("Clipboard Contents:\n", result)


if __name__ == '__main__':
    unittest.main()
