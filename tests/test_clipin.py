import sys
import unittest
import clipin
from clipin import ClipboardError


class TestClipin(unittest.TestCase):

    def test_text_plain_roundtrip(self):
        text = "Hello from clipin!"
        clipin.copy(text)
        data = clipin.paste('text/plain')
        self.assertIn("Hello", data)

    def test_available_formats_returns_list(self):
        formats = clipin.available_formats()
        self.assertIsInstance(formats, list)
        print("Available Formats are : ", formats)

    @unittest.skipIf(not sys.platform.startswith("win"), "Skipping binary format test if not on Windows")
    def test_set_invalid_format(self):
        with self.assertRaises(ClipboardError):
            clipin.copy(b'unsupported data', 'application/unknown')

    def test_get_returns_dict(self):
        clipin.copy("Sample Text")
        result = clipin.paste()
        self.assertIsInstance(result, dict)

        result = clipin.paste('text/plain')
        self.assertIsInstance(result, str)

        result = clipin.paste(0)
        self.assertIsInstance(result, dict)


        print("Clipboard Contents:\n", result)

    def test_image_roundtrip(self):
        import os
        image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
        if not os.path.exists(image_path):
            self.skipTest("test_image.png not found, skipping image roundtrip test.")

        with open(image_path, 'rb') as f:
            image_data = f.read()

        clipin.copy(image_data, 'image/png')
        pasted_data = clipin.paste('image/png')
        # save pasted data to a file for manual verification if needed
        # with open(os.path.join(os.path.dirname(__file__), 'pasted_image.png'), 'wb') as f:
        #     f.write(pasted_data[:-1])  # Remove the last byte added during copy on Windows
        self.assertEqual(image_data, pasted_data[:-1])  # Compare without the last byte. Added during copy on Windows


if __name__ == '__main__':
    # clipin._use_appkit = False
    unittest.main()

