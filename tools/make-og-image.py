#!/usr/bin/env python3
"""Generate AIOMetadata social preview card (1200x630) for Open Graph / Twitter.

Reproduces the project's own brand: the real magnifying-glass-over-circuit
logo from public/logo.png, the theme color from index.html (#01b4e4) and the
site's own copy ("Configure your AIOMetadata Addon for Stremio" — the existing
meta description). No invented UI tropes, no marketing fluff.

Portable: fonts resolve via AIO_FONT_DIR -> ./fonts -> ~/.fonts -> system dirs.
Usage: python3 tools/make-og-image.py [output.png]
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
THEME = (1, 180, 228)          # #01b4e4 from index.html theme-color
INK = (23, 32, 38)             # near-black text
GREY = (100, 116, 130)         # muted tagline

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_font(candidates, size):
    paths = []
    env = os.environ.get("AIO_FONT_DIR")
    if env:
        paths.append(env)
    paths += [
        os.path.join(REPO_ROOT, "fonts"),
        os.path.expanduser("~/.fonts"),
        "/usr/share/fonts/truetype/montserrat",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
    ]
    for base in paths:
        for name in candidates:
            p = os.path.join(base, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    raise SystemExit(f"None of {candidates} found; set AIO_FONT_DIR")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "public", "og-image.png")

    logo_path = os.path.join(REPO_ROOT, "public", "logo.png")
    if not os.path.exists(logo_path):
        raise SystemExit(f"logo not found at {logo_path}")

    # Real logo asset (RGBA, transparent margins around the actual mark).
    raw = Image.open(logo_path).convert("RGBA")
    bbox = raw.getbbox()
    mark = raw.crop(bbox)

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Thin brand-accent bar at the very top (site theme color).
    draw.rectangle([0, 0, W, 10], fill=THEME)

    # Logo mark, centered upper area.
    mark_w = 300
    mark_h = int(mark.height * mark_w / mark.width)
    mark_img = mark.resize((mark_w, mark_h), Image.LANCZOS)
    img.paste(mark_img, ((W - mark_w) // 2, 96), mark_img)

    # Wordmark + real site copy.
    font_brand = find_font(["Montserrat-SemiBold.ttf", "Montserrat-Bold.ttf", "DejaVuSans-Bold.ttf"], 76)
    font_tag = find_font(["Montserrat-Medium.ttf", "Montserrat-Regular.ttf", "DejaVuSans.ttf"], 34)

    word = "AIOMetadata"
    w_w = draw.textlength(word, font=font_brand)
    draw.text(((W - w_w) / 2, 440), word, font=font_brand, fill=INK)

    tag = "Configure your AIOMetadata Addon for Stremio"
    t_w = draw.textlength(tag, font=font_tag)
    draw.text(((W - t_w) / 2, 548), tag, font=font_tag, fill=GREY)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
