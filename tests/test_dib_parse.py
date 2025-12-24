import clipin
from pathlib import Path


def test_parse_dib_files_to_png():
    files = [
        Path("tests/clipboard_data_image_x-win-dib.bin"),
        Path("tests/clipboard_data_image_x-win-dibv5.bin"),
    ]
    for p in files:
        data = p.read_bytes()
        out = clipin._parse_dib_to_png(data, format='PNG')
        assert isinstance(out, (bytes, bytearray))
        # PNG signature
        assert out[:8] == b"\x89PNG\r\n\x1a\n"

