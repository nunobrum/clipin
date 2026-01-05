import sys
import os
sys.path.append(os.path.abspath('..'))
import unittest
import clipin
from clipin import ClipboardError
import io
try:
    from PIL import Image
except ImportError:
    compare_images = None
    Image = None
else:
    def compare_images(self, img1, img2):
        img1 = Image.open(io.BytesIO(img1))
        img2 = Image.open(io.BytesIO(img2))
        self.assertEqual(img1.size, img2.size)
        compare_RGB_only = img1.mode != img2.mode
        for x in range(img1.width):
            for y in range(img1.height):
                # Only compare RGB, ignore alpha channel differences
                if compare_RGB_only:
                    self.assertEqual(img1.getpixel((x, y))[0:3], img2.getpixel((x, y))[0:3])
                else:
                    self.assertEqual(img1.getpixel((x, y)), img2.getpixel((x, y)))


class TestClipin(unittest.TestCase):

    @unittest.skipIf(not clipin.capabilities()["textplain"], "Skipping test if clipboard is not available")
    def test_text_plain_roundtrip(self):
        text = "Hello from clipin!"
        clipin.copy(text)
        data = clipin.paste('text/plain')
        self.assertIn("Hello", data)

    @unittest.skipIf(not clipin.capabilities()["mime"], "Skipping test if clipboard is not available")
    def test_text_html_roundtrip(self):
        text = "<b>Hello from clipin!</b>"  # The native formats differ a lot. The goal is to be able to store, and to be able to read the native format. Cannot test all of that.
        clipin.copy(text, 'text/html')
        data = clipin.paste('text/html')
        self.assertIn("Hello from clipin!", data)

    def test_capabilities_returns_dict(self):
        caps = clipin.capabilities()
        self.assertIsInstance(caps, dict)
        print("Capabilities are : ", caps)        

    def test_available_formats_returns_list(self):
        formats = clipin.available_formats()
        self.assertIsInstance(formats, list)
        print("Available Formats are : ", formats)

    def test_set_invalid_format(self):
        with self.assertRaises(ClipboardError):
            clipin.copy(b'unsupported data', 'application/unknown')

    @unittest.skipIf(not clipin.capabilities()["textplain"], "Skipping test if clipboard is not available")
    def test_get_returns_dict(self):
        clipin.copy("Sample Text")
        result = clipin.paste()
        self.assertIsInstance(result, dict)

        result = clipin.paste('text/plain')
        self.assertIsInstance(result, str)

        result = clipin.paste(0)
        self.assertIsInstance(result, dict)

        print("Clipboard Contents:\n", result)

    @unittest.skipIf(not clipin.capabilities()["mime"], "Skipping image roundtrip test if image support is not available")
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
        with open(os.path.join(os.path.dirname(__file__), 'pasted_image.png'), 'wb') as f:
            f.write(pasted_data)  # Remove the last byte added during copy on Windows
        # compare it two images are identical, but cannot guarantee byte-for-byte due to possible metadata differences
        # need to use image comparison instead of byte comparison
        if compare_images:
            compare_images(self, image_data, pasted_data)



if __name__ == '__main__':
    # clipin._use_appkit = False
    unittest.main()

