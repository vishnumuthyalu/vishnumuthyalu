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
MAX_COLS = 96
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
    return Image.fromarray(np.minimum(np.array(img), np.array(edge)))


def to_rows(img: Image.Image) -> list[str]:
    img = img.convert("L")
    iw, ih = img.size
    font_px = AREA_W / (MAX_COLS * CHAR_ASPECT)
    cols = MAX_COLS
    rows = round(ih / iw * cols * CHAR_ASPECT / LINE)
    max_rows = int(AREA_H / (font_px * LINE))
    if rows > max_rows:  # tall image: shrink both so it fits the frame
        scale = max_rows / rows
        rows, cols = max_rows, max(20, int(cols * scale))
    px = np.asarray(img.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    idx = ((1.0 - px) * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    src = Image.open(SRC) if SRC.exists() else monogram()
    rows = to_rows(src)
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()

    font_px = AREA_W / (MAX_COLS * CHAR_ASPECT)
    cw, lh = font_px * CHAR_ASPECT, font_px * LINE
    width_chars = max(len(r) for r in rows)
    block_w, block_h = width_chars * cw, len(rows) * lh
    ox = AREA_X + (AREA_W - block_w) / 2
    oy = AREA_Y + (AREA_H - block_h) / 2

    defs, body = [], []
    for n, r in enumerate(rows):
        if not r.strip():
            continue
        y = oy + n * lh
        begin = START + n * ROW_STAGGER
        rw = len(r) * cw
        defs.append(
            f'<clipPath id="r{n}"><rect x="{ox:.2f}" y="{y:.2f}" width="0" height="{lh + .5:.2f}">'
            f'<animate attributeName="width" from="0" to="{rw + 2:.2f}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        body.append(
            f'<text clip-path="url(#r{n})" x="{ox:.2f}" y="{y + font_px * 0.85:.2f}" '
            f'textLength="{rw:.2f}" lengthAdjust="spacing">{esc(r)}</text>'
        )
        # block cursor riding the wipe edge
        body.append(
            f'<rect x="{ox:.2f}" y="{y:.2f}" width="{cw:.2f}" height="{lh:.2f}" fill="{ACCENT}" opacity="0">'
            f'<set attributeName="opacity" to=".9" begin="{begin:.3f}s"/>'
            f'<animate attributeName="x" from="{ox:.2f}" to="{ox + rw:.2f}" begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.3f}s"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">
<style>text {{ font-family: {FONT}; font-size: {font_px:.2f}px; fill: {INK}; white-space: pre; }}
.bar {{ font-size: 11px; fill: {DIM}; }}</style>
<defs>{"".join(defs)}</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M.5 30.5h{W - 1}" stroke="{BORDER}"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" text-anchor="middle" class="bar">cat portrait.txt</text>
<g xml:space="preserve">{"".join(body)}</g>
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name}: {len(rows)} rows x {width_chars} cols ({'photo' if SRC.exists() else 'monogram placeholder'})")


if __name__ == "__main__":
    main()
