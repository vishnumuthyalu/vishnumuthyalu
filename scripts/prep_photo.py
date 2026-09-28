"""Prep a portrait for ASCII conversion (run once per photo, locally).

    python scripts/prep_photo.py path/to/photo.jpg

1. remove the background (rembg) so only you print
2. CLAHE local-contrast boost so a flatly-lit face gets real shadows
3. composite onto pure white -> background maps to the blank end of the ramp
Writes source-prepped.png (grayscale) in the repo root.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def main(src: str) -> None:
    img = Image.open(src).convert("RGB")
    cut = remove(img)  # RGBA, transparent background

    rgba = np.array(cut)
    alpha = rgba[..., 3:4].astype(np.float32) / 255.0
    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    white = np.full_like(gray, 255.0)
    out = gray * alpha[..., 0] + white * (1 - alpha[..., 0])

    # crop to the subject's bounding box (+ a little margin)
    ys, xs = np.where(alpha[..., 0] > 0.1)
    if len(xs):
        m = 20
        y0, y1 = max(ys.min() - m, 0), min(ys.max() + m, out.shape[0])
        x0, x1 = max(xs.min() - m, 0), min(xs.max() + m, out.shape[1])
        out = out[y0:y1, x0:x1]

    Image.fromarray(out.clip(0, 255).astype(np.uint8), "L").save(OUT)
    print(f"wrote {OUT.name} {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    main(sys.argv[1])
