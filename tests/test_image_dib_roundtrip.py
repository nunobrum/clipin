import io
import os
import sys
from pathlib import Path
import unittest

import clipin

# helper to check PNG signature
def is_png(b: bytes) -> bool:
    return b is not None and b[:8] == b"\x89PNG\r\n\x1a\n"

class TestImageDIBRoundtrip(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent
        self.samples = [
            'pattern.png',
            'pattern.bmp',
            'pattern.tiff',
            'test_image.png',
            'test_image.bmp',
            'test_image.tiff',
        ]

    def test_dib_binaries_convert_to_png(self):
        # existing raw DIB sample binaries
        for name in ('clipboard_data_image_x-win-dib.bin', 'clipboard_data_image_x-win-dibv5.bin'):
            p = self.root / name
            raw = p.read_bytes()
            out = clipin._parse_dib_to_png(raw, format='PNG')
            self.assertTrue(is_png(out), f"DIB binary {name} did not convert to PNG")

    def test_image_to_dib_and_back(self):
        # for each sample image, convert to DIB and back to PNG
        for name in self.samples:
            p = self.root / name
            img_bytes = p.read_bytes()
            # convert image bytes to DIB bytes
            dib = clipin.convert_image_to_dib_bytes(img_bytes, clipin.CF_DIB)
            self.assertIsInstance(dib, (bytes, bytearray))
            # convert DIB back to PNG bytes
            out = clipin._parse_dib_to_png(dib, format='PNG')
            self.assertTrue(is_png(out), f"Roundtrip for {name} did not produce PNG")

    def test_dibv5_roundtrip(self):
        # test CF_DIBV5 conversion specifically
        for name in ('pattern.png', 'test_image.png'):
            p = self.root / name
            img_bytes = p.read_bytes()
            dibv5 = clipin.convert_image_to_dib_bytes(img_bytes, clipin.CF_DIBV5)
            self.assertIsInstance(dibv5, (bytes, bytearray))
            out = clipin._parse_dib_to_png(dibv5, format='PNG')
            self.assertTrue(is_png(out), f"DIBV5 roundtrip for {name} failed")


if __name__ == '__main__':
    unittest.main()

