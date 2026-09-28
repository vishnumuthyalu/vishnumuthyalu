"""Convert source-prepped.png -> ascii-portrait.svg (monochrome, types itself in).

    python scripts/make_ascii_svg.py

If source-prepped.png doesn't exist yet, a "VM" monogram is used as a stand-in
so the README still has something in the portrait slot.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii-portrait.svg"

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = background
W, H = 370, 380
BG, INK, DIM, BORDER, ACCENT = "#0d1117", "#c9d1d9", "#6e7681", "#30363d", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

AREA_X, AREA_Y, AREA_W, AREA_H = 16, 44, W - 32, H - 58
COLS = 104         # grid width; font size is derived so the block fills the frame
CROP_ASPECT = 0.92 # keep the top (h = w * this): head and shoulders
# Light ink on a dark terminal: dense glyphs read BRIGHT, so map bright skin to dense
# glyphs and dark hair/clothes to sparse ones. The background is blanked via the mask.
INVERT = True
GAMMA = 1.15
CHAR_ASPECT = 0.6  # monospace glyph width / font-size
LINE = 1.1         # line height / font-size
ROW_DUR, ROW_STAGGER, START = 0.22, 0.045, 0.3


def monogram() -> Image.Image:
    img = Image.new("L", (900, 700), 255)
    d = ImageDraw.Draw(img)
    font = None
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        try:
            font = ImageFont.truetype(p, 460)
            break
        except OSError:
            continue
    d.text((450, 350), "VM", fill=0, font=font or ImageFont.load_default(), anchor="mm")
    # soft edge so the density ramp gets a gradient instead of a hard cutout
    edge = img.filter(ImageFilter.GaussianBlur(10))
    g = np.minimum(np.array(img), np.array(edge))
    return Image.fromarray(np.dstack([255 - g, np.where(g < 250, 255, 0)]).astype(np.uint8), "LA")


def to_rows(img: Image.Image) -> tuple[list[str], float]:
    img = img.convert("LA")
    iw, ih = img.size
    if ih > iw * CROP_ASPECT:
        img = img.crop((0, 0, iw, int(iw * CROP_ASPECT)))
        iw, ih = img.size
    cols = COLS
    rows = round(ih / iw * cols * CHAR_ASPECT / LINE)
    font_px = min(AREA_W / (cols * CHAR_ASPECT), AREA_H / (rows * LINE))
    arr = np.asarray(img.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    lum, mask = arr[..., 0], arr[..., 1]
    # stretch contrast using only subject pixels (background white would skew it)
    sub = lum[mask > 0.5]
    if sub.size:
        lo, hi = np.percentile(sub, [3, 99])
        lum = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1)
    ink = lum if INVERT else 1.0 - lum
    ink = np.clip(ink, 0, 1) ** GAMMA
    # subject always gets at least the faintest glyph so dark hair/clothes keep a silhouette
    ink = np.where(mask > 0.5, np.maximum(ink, 1.0 / (len(RAMP) - 1)), 0.0)
    idx = (ink * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx], font_px


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    src = Image.open(SRC) if SRC.exists() else monogram()
    rows, font_px = to_rows(src)
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()

    cw, lh = font_px * CHAR_ASPECT, font_px * LINE
    width_chars = max(len(r) for r in rows)
    block_w, block_h = width_chars * cw, len(rows) * lh
    ox = AREA_X + (AREA_W - block_w) / 2
    oy = AREA_Y + (AREA_H - block_h) / 2

    body = []
    for n, r in enumerate(rows):
        if not r.strip():
            continue
        # one element per row; the wipe is a CSS clip animation staggered by --i
        body.append(
            f'<text y="{oy + n * lh + font_px * 0.85:.2f}" textLength="{len(r) * cw:.2f}" '
            f'style="--i:{n}">{esc(r)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">
<style>text {{ font-family: {FONT}; font-size: {font_px:.2f}px; fill: {INK}; white-space: pre; }}
.a text {{ clip-path: inset(0 100% 0 0); animation: type {ROW_DUR}s steps(24, end) forwards;
  animation-delay: calc({START}s + var(--i) * {ROW_STAGGER}s); }}
@keyframes type {{ to {{ clip-path: inset(0 0 0 0); }} }}
.bar {{ font-size: 11px; fill: {DIM}; }}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M.5 30.5h{W - 1}" stroke="{BORDER}"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" text-anchor="middle" class="bar">cat portrait.txt</text>
<g class="a" xml:space="preserve" transform="translate({ox:.2f} 0)">{"".join(body)}</g>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name}: {len(rows)} rows x {width_chars} cols ({'photo' if SRC.exists() else 'monogram placeholder'})")


if __name__ == "__main__":
    main()
