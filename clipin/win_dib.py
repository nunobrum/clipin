# Windows DIB (Device Independent Bitmap) handling for clipboard operations.
# This library converts between raw DIB data and standard BMP files for use with ctypes
# and Pillow.
import ctypes
from typing import Optional
from PIL import Image as ImageModule
from PIL.Image import Image as ImageClass
import io

CF_DIB = 8  # A memory object containing a BITMAPINFO structure followed by the bitmap bits.
CF_DIBV5 = 17  # A memory object containing a BITMAPV5HEADER structure followed by the bitmap color

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1  # Ensure no alignment padding; BITMAPFILEHEADER is packed to 14 bytes on disk
    _fields_ = [
        ("bfType", ctypes.c_ushort),
        ("bfSize", ctypes.c_ulong),
        ("bfReserved1", ctypes.c_ushort),
        ("bfReserved2", ctypes.c_ushort),
        ("bfOffBits", ctypes.c_ulong),
    ]


class BITMAPCOREHEADER(ctypes.Structure):
    _fields_ = [
        ("bcSize", ctypes.c_ulong),
        ("bcWidth", ctypes.c_ushort),
        ("bcHeight", ctypes.c_ushort),
        ("bcPlanes", ctypes.c_ushort),
        ("bcBitCount", ctypes.c_ushort),
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_ulong),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", ctypes.c_ushort),
        ("biBitCount", ctypes.c_ushort),
        ("biCompression", ctypes.c_ulong),
        ("biSizeImage", ctypes.c_ulong),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", ctypes.c_ulong),
        ("biClrImportant", ctypes.c_ulong),
    ]


class RGBQUAD(ctypes.Structure):
    _fields_ = [
        ("rgbBlue", ctypes.c_ubyte),
        ("rgbGreen", ctypes.c_ubyte),
        ("rgbRed", ctypes.c_ubyte),
        ("rgbReserved", ctypes.c_ubyte),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", RGBQUAD * 1),
    ]


class CIEXYZ(ctypes.Structure):
    _fields_ = [
        ("ciexyzX", ctypes.c_long),
        ("ciexyzY", ctypes.c_long),
        ("ciexyzZ", ctypes.c_long),
        ]


class CIEXYZTRIPLE(ctypes.Structure):
    _fields_ = [
        ("ciexyzRed", CIEXYZ),
        ("ciexyzGreen", CIEXYZ),
        ("ciexyzBlue", CIEXYZ),
        ]

class BITMAPV5HEADER(ctypes.Structure):

    _fields_ = [
        ("bV5Size", ctypes.c_ulong),
        ("bV5Width", ctypes.c_long),
        ("bV5Height", ctypes.c_long),
        ("bV5Planes", ctypes.c_ushort),
        ("bV5BitCount", ctypes.c_ushort),
        ("bV5Compression", ctypes.c_ulong),
        ("bV5SizeImage", ctypes.c_ulong),
        ("bV5XPelsPerMeter", ctypes.c_long),
        ("bV5YPelsPerMeter", ctypes.c_long),
        ("bV5ClrUsed", ctypes.c_ulong),
        ("bV5ClrImportant", ctypes.c_ulong),
        ("bV5RedMask", ctypes.c_ulong),
        ("bV5GreenMask", ctypes.c_ulong),
        ("bV5BlueMask", ctypes.c_ulong),
        ("bV5AlphaMask", ctypes.c_ulong),
        ("bV5CSType", ctypes.c_ulong),
        ("bV5Endpoints", CIEXYZTRIPLE),
        ("bV5GammaRed", ctypes.c_ulong),
        ("bV5GammaGreen", ctypes.c_ulong),
        ("bV5GammaBlue", ctypes.c_ulong),
        ("bV5Intent", ctypes.c_ulong),
        ("bV5ProfileData", ctypes.c_ulong),
        ("bV5ProfileSize", ctypes.c_ulong),
        ("bV5Reserved", ctypes.c_ulong),
    ]


def convert_dib_to_image(dib_data: bytes) -> Optional[ImageClass]:
    """Convert raw DIB data (BITMAPINFOHEADER / BITMAPV5HEADER + pixel data) into a standard BMP
    file in memory and re-encode it using Pillow to the requested format (default PNG).

    The clipboard CF_DIB and CF_DIBV5 formats provide the DIB (bitmap info header + palette + bits)
    without the 14-byte BITMAPFILEHEADER. Pillow expects a BMP file, so we prepend a proper
    BITMAPFILEHEADER computed from the DIB header size and palette.

    On any parsing or decoding error the original data is returned unchanged to avoid
    breaking callers that expect the raw DIB bytes.
    """
    try:
        if not isinstance(dib_data, (bytes, bytearray)) or len(dib_data) < ctypes.sizeof(BITMAPINFOHEADER):
            return None

        # Read header size (first 4 bytes, little endian)
        header_size = int.from_bytes(dib_data[0:4], 'little')

        # Default values
        palette_entry_size = 4  # RGBQUAD size for BITMAPINFOHEADER and V5
        palette_count = 0

        if header_size == 12:
            # BITMAPCOREHEADER (OS/2 BMP)
            # biBitCount is at offset 10 (2 bytes)
            if len(dib_data) < 12:
                return None
            bpp = int.from_bytes(dib_data[10:12], 'little')
            palette_entry_size = 3  # RGBTRIPLE
            if bpp <= 8:
                palette_count = 1 << bpp
        else:
            # BITMAPINFOHEADER (>=40) or BITMAPV5HEADER (124)
            if len(dib_data) < 16:
                return None
            # biBitCount at offset 14 (2 bytes)
            bpp = int.from_bytes(dib_data[14:16], 'little')
            # biClrUsed at offset 32 (4 bytes) is optional - used palette entries
            bi_clr_used = 0
            if len(dib_data) >= 36:
                bi_clr_used = int.from_bytes(dib_data[32:36], 'little')

            if bi_clr_used:
                palette_count = bi_clr_used
            elif bpp <= 8:
                palette_count = 1 << bpp
            else:
                palette_count = 0

        palette_size = palette_count * palette_entry_size

        # Calculate the pixel dib_data offset in the BMP file: file header (14) + DIB header + palette
        offset = ctypes.sizeof(BITMAPFILEHEADER) + header_size + palette_size
        file_size = ctypes.sizeof(BITMAPFILEHEADER) + len(dib_data)

        # Build BITMAPFILEHEADER
        bmp_header = BITMAPFILEHEADER()
        bmp_header.bfType = 0x4D42  # 'BM'
        bmp_header.bfSize = file_size
        bmp_header.bfReserved1 = 0
        bmp_header.bfReserved2 = 0
        bmp_header.bfOffBits = offset

        bmp_bytes = bytes(bmp_header) + bytes(dib_data)

        image = ImageModule.open(io.BytesIO(bmp_bytes))
        return image
    except Exception:
        # Keep original dib_data if anything goes wrong
        return None


def convert_image_to_dib_bytes(image_data, dib_format: int) -> Optional[bytes]:
    """Convert a PIL Image to DIB bytes suitable for clipboard CF_DIB format.

    :param image: PIL Image to convert.
    :param dib_format: DIB format to convert to (e.g., CF_DIB or CF_DIBV5).
    :return: Bytes representing the DIB (BITMAPINFOHEADER + pixel data).
    """
    try:

        if not isinstance(image_data, (bytes, bytearray)):
            return image_data

        # Load BMP data into a PIL Image
        with io.BytesIO(image_data) as bmp_io:
            img = ImageModule.open(bmp_io)
            img = img.convert("RGBA")  # Ensure 32-bit RGBA for DIBV5

            # Save image as BMP into a BytesIO buffer
            with io.BytesIO() as output:
                img.save(output, format='BMP')
                bmp_bytes = output.getvalue()

        # Strip the 14-byte BITMAPFILEHEADER to get DIB data
        bmp_pixels = bmp_bytes[ctypes.sizeof(BITMAPFILEHEADER):]
        if dib_format == CF_DIBV5:
            # For CF_DIBV5, ensure we have a BITMAPV5HEADER
            dib_header = BITMAPV5HEADER()
            dib_header.bV5Size = ctypes.sizeof(BITMAPV5HEADER)
            dib_header.bV5Width = img.width
            dib_header.bV5Height = img.height
            dib_header.bV5Planes = 1
            dib_header.bV5BitCount = 32
            dib_header.bV5Compression = 0  # BI_RGB
            dib_header.bV5SizeImage = len(bmp_pixels)
            dib_header.bV5XPelsPerMeter = 0
            dib_header.bV5YPelsPerMeter = 0
            dib_header.bV5ClrUsed = 0
            dib_header.bV5ClrImportant = 0
            dib_header.bV5RedMask = 0x00FF0000
            dib_header.bV5GreenMask = 0x0000FF00
            dib_header.bV5BlueMask = 0x000000FF
            dib_header.bV5AlphaMask = 0xFF000000
            dib_header.bV5CSType = 0x73524742  # LCS_sRGB
            dib_header.bV5Endpoints = CIEXYZTRIPLE()
            dib_header.bV5GammaRed = 0
            dib_header.bV5GammaGreen = 0
            dib_header.bV5GammaBlue = 0
            dib_header.bV5Intent = 4  # LCS_GM_GRAPHICS
            dib_header.bV5ProfileData = 0
            dib_header.bV5ProfileSize = 0
            dib_header.bV5Reserved = 0
            return bytes(dib_header) + bmp_pixels
        else:
            # For CF_DIB, return the DIB data as is
            return bmp_pixels

    except Exception:
        # If any error occurs, return None
        return None


def parse_dib_to_png(data: bytes, format: str = None) -> bytes:
    """Wrapper that converts raw DIB bytes to an encoded image (PNG by default).

    Returns original data on failure to preserve previous behavior.
    """
    try:
        img = convert_dib_to_image(data)
        if img is None:
            return data
        out = io.BytesIO()
        out_format = format if format is not None else 'PNG'
        img.save(out, format=out_format)
        return out.getvalue()
    except Exception:
        return data

