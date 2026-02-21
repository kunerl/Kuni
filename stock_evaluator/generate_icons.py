"""Generiert PNG-Icons aus der SVG-Datei für die PWA.

Benötigt: pip install cairosvg   (oder manuell erstellen)
Fallback: Erstellt einfache PNG-Icons ohne externe Abhängigkeiten.
"""

import struct
import zlib
from pathlib import Path


def create_png(width: int, height: int, path: Path):
    """Erstellt ein einfaches PNG-Icon mit Chart-Motiv."""

    def make_pixel(r, g, b, a=255):
        return bytes([r, g, b, a])

    bg = make_pixel(13, 17, 23)
    inner_bg = make_pixel(22, 27, 34)
    green = make_pixel(35, 134, 54)
    red = make_pixel(218, 54, 51)
    blue = make_pixel(88, 166, 255)

    raw_data = bytearray()

    # Bar positions (normalized to 0-1 range)
    bars = [
        (0.156, 0.625, 0.195, red),    # bar 1
        (0.313, 0.508, 0.313, red),     # bar 2
        (0.469, 0.391, 0.430, green),   # bar 3
        (0.625, 0.273, 0.547, green),   # bar 4
        (0.781, 0.195, 0.625, green),   # bar 5
    ]

    for y in range(height):
        raw_data.append(0)  # filter byte
        ny = y / height
        for x in range(width):
            nx = x / width

            # Rounded outer corners
            margin = 0.0625
            corner_r = 0.188
            pixel = bg

            in_inner = margin < nx < (1 - margin) and margin < ny < (1 - margin)
            if in_inner:
                pixel = inner_bg

                # Draw bars
                for bx, by, bh, color in bars:
                    bar_w = 0.109
                    if bx <= nx <= bx + bar_w and by <= ny <= by + bh:
                        pixel = color
                        break

            raw_data.extend(pixel)

    # Create PNG file
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw_data), 9)

    with open(path, "wb") as f:
        f.write(signature)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", compressed))
        f.write(chunk(b"IEND", b""))


if __name__ == "__main__":
    static = Path(__file__).parent / "static"
    print("Generiere icon-192.png ...")
    create_png(192, 192, static / "icon-192.png")
    print("Generiere icon-512.png ...")
    create_png(512, 512, static / "icon-512.png")
    print("Fertig!")
