"""
Generate brand icon/logo PNGs for the Desk integration.

Renders the official Material Design Icons ``mdi:desk`` glyph (the same icon
shown for entities in the Home Assistant UI) in the brand color and writes
the standard image filenames into ``custom_components/desk_integration/brand/``.

Run with: ``python3 scripts/generate_brand_images.py``
"""

from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

# mdi:desk path (https://pictogrammers.com/library/mdi/icon/desk/)
MDI_DESK_PATH = (
    "M3 6H21C21.55 6 22 6.45 22 7C22 7.55 21.55 8 21 8V19H19V17H15V19H13V8H5V19H3"
    "V8C2.45 8 2 7.55 2 7C2 6.45 2.45 6 3 6M16 10.5V11H18V10.5C18 10.22 17.78 10 "
    "17.5 10H16.5C16.22 10 16 10.22 16 10.5M16 14.5V15H18V14.5C18 14.22 17.78 14 "
    "17.5 14H16.5C16.22 14 16 14.22 16 14.5Z"
)

HA_BLUE = "#03A9F4"
WHITE = "#FFFFFF"

BRAND_DIR = Path(__file__).resolve() / "brand"


def _render_desk(size: int, color: str) -> Image.Image:
    """Render the mdi:desk glyph centered in a transparent square canvas.

    The glyph is inset slightly so it doesn't touch the canvas edges, which
    matches how Home Assistant brand icons are usually framed.
    """
    inset_pct = 0.10  # 10% margin around the glyph
    glyph_size = round(size * (1 - 2 * inset_pct))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="{glyph_size}" height="{glyph_size}">'
        f'<path d="{MDI_DESK_PATH}" fill="{color}"/></svg>'
    )
    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        output_width=glyph_size,
        output_height=glyph_size,
    )
    glyph = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = (size - glyph_size) // 2
    canvas.paste(glyph, (offset, offset), glyph)
    return canvas


def _logo(size_w: int, size_h: int, color: str) -> Image.Image:
    """Compose a logo: mdi:desk glyph on the left, 'Desk' wordmark on the right."""
    img = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    glyph = _render_desk(size_h, color)
    img.paste(glyph, (0, 0), glyph)

    draw = ImageDraw.Draw(img)
    text = "Desk"
    font_size = round(size_h * 0.45)
    font: ImageFont.ImageFont | ImageFont.FreeTypeFont
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if Path(candidate).exists():
            font = ImageFont.truetype(candidate, font_size)
            break
    else:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_h = bbox[3] - bbox[1]
    text_x = size_h + round(size_h * 0.05)
    text_y = (size_h - text_h) // 2 - bbox[1]
    draw.text((text_x, text_y), text, font=font, fill=color)
    return img


def main() -> None:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)

    # Icons: square, light + dark variants, @1x (256) and @2x (512).
    for scale, suffix in ((1, ""), (2, "@2x")):
        size = 256 * scale
        _render_desk(size, HA_BLUE).save(BRAND_DIR / f"icon{suffix}.png")
        _render_desk(size, WHITE).save(BRAND_DIR / f"dark_icon{suffix}.png")

    # Logos: wide aspect with wordmark.
    for scale, suffix in ((1, ""), (2, "@2x")):
        w, h = 640 * scale, 256 * scale
        _logo(w, h, HA_BLUE).save(BRAND_DIR / f"logo{suffix}.png")
        _logo(w, h, WHITE).save(BRAND_DIR / f"dark_logo{suffix}.png")

    print(f"Wrote brand images to {BRAND_DIR}")


if __name__ == "__main__":
    main()
