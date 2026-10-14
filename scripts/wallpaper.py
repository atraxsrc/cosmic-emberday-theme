#!/usr/bin/env python3
"""Recolour one wallpaper with the repo palette.

    python3 scripts/wallpaper.py night [--accent NAME] GREY.png OUT.png
    python3 scripts/wallpaper.py day   [--accent NAME] GREY.png OUT.png
    python3 scripts/wallpaper.py night --v1 --accent Amber ember-eagle-v1.png OUT.png

GREY is the cover-cropped grey render that scripts/wallpaper.sh prepares (light
subject on dark for night, dark subject on light for day). --v1 instead reads
a wallpaper made by the first, two-tone lookup and recovers its grey levels, so
the shipped wallpapers can be redone without the cool-wallpapers sources.

The palette is read from backgrounds/*.gpl. The subject stays calm, as the
palette asks: neutrals for the big shapes, one supporting colour (--accent,
slate blue unless named) for the body, and ember small and loud near the top.
Each pixel gets an ink level, 0 on the paper and 1 on the strongest line, and
its rank inside the subject runs it along one ramp:

    window   the paper, flat, so it lands exactly on the window colour
    comment  faint shading
    muted    shadows and fine lines
    accent   the body of the subject
    ember    the brightest (night) or boldest (day) strokes
    text     the strongest lines

Blends between roles are mixed in OKLab and every role holds a flat band,
so each one lands on its exact hex, and the corners stay on the window.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

W, H = 3840, 2160
ACCENTS = ["Brick", "Ember", "Amber", "Moss", "Verdigris", "Slate blue", "Heather"]

# The first lookup of scripts/wallpaper.sh, as (rows, from, to); used by --v1.
V1 = {
    "night": [(48, "15171C", "15171C"), (42, "15171C", "2A2F38"), (70, "2A2F38", "7C8290"),
              (60, "7C8290", "E8713A"), (36, "E8713A", "F1D9C8")],
    "day": [(100, "2B2E36", "6B6F78"), (50, "6B6F78", "A4441A"), (40, "A4441A", "D4CFC6"),
            (15, "D4CFC6", "E9E6DF"), (51, "E9E6DF", "E9E6DF")],
}


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def palette(root):
    gpl = glob.glob(os.path.join(root, "backgrounds", "*.gpl"))
    assert len(gpl) == 1, f"want one .gpl in backgrounds/, found {gpl}"
    pal = {}
    for line in open(gpl[0]):
        p = line.split()
        if len(p) >= 4 and all(x.isdigit() for x in p[:3]):
            pal[" ".join(p[3:-1])] = np.array([int(x) for x in p[:3]], dtype=np.float64)
    return pal


def to_lab(c):
    c = c / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(c @ m1.T) @ m2.T


def from_lab(L):
    m2i = np.array([[1.0, 0.3963377774, 0.2158037573],
                    [1.0, -0.1055613458, -0.0638541728],
                    [1.0, -0.0894841775, -1.2914855480]])
    m1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                    [-1.2684380046, 2.6097574011, -0.3413193965],
                    [-0.0041960863, -0.7034186147, 1.7076147010]])
    c = np.clip((L @ m2i.T) ** 3 @ m1i.T, 0, 1)
    c = np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.rint(c * 255).clip(0, 255).astype(np.uint8)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ink_from_grey(mode, path):
    g = np.asarray(Image.open(path).convert("I;16"), dtype=np.float32) / 65535
    if g.shape != (H, W):
        sys.exit(f"{path} is {g.shape[1]}x{g.shape[0]}, want {W}x{H}")
    return g if mode == "night" else 1 - g


def ink_from_v1(mode, path):
    """Invert the two-tone lookup: find each colour's row, row/255 is the grey."""
    rows = []
    for n, a, b in V1[mode]:
        a, b = rgb(a), rgb(b)
        rows += [a + (b - a) * i / max(n - 1, 1) for i in range(n)]
    rows = np.array(rows)
    fine = np.concatenate([rows[i] + (rows[i + 1] - rows[i]) * np.linspace(0, 1, 16, endpoint=False)[:, None]
                           for i in range(len(rows) - 1)] + [rows[-1:]])
    grey_of_fine = np.arange(len(fine)) / 16 / 255
    img = np.asarray(Image.open(path).convert("RGB"))
    if img.shape[:2] != (H, W):
        sys.exit(f"{path} is {img.shape[1]}x{img.shape[0]}, want {W}x{H}")
    flat = img.reshape(-1, 3)
    keys = (flat[:, 0].astype(np.int32) << 16) | (flat[:, 1].astype(np.int32) << 8) | flat[:, 2]
    uniq, inv = np.unique(keys, return_inverse=True)
    ucol = np.stack([uniq >> 16, (uniq >> 8) & 255, uniq & 255], 1).astype(np.float64)
    d = ((ucol[:, None, :] - fine[None, :, :]) ** 2).sum(-1)
    near = d.argmin(1)
    worst = np.sqrt(d[np.arange(len(ucol)), near]).max()
    if worst > 3:
        sys.exit(f"{path}: a colour sits {worst:.1f} off the {mode} lookup, not a v1 render")
    g = grey_of_fine[near][inv].reshape(H, W).astype(np.float32)
    return g if mode == "night" else 1 - g


def rank(ink, subject):
    """Spread the subject's ink evenly over 0.2-1 by its own distribution (ties
    take their middle rank), so a faint render and a bold one both run the whole
    ramp and every role lands on part of the subject."""
    bins = np.clip((ink * 4095).astype(np.int32), 0, 4095)
    n = np.bincount(bins[subject], minlength=4096).astype(np.float64)
    mid = (np.cumsum(n) - n / 2) / n.sum()
    return np.where(subject, 0.2 + 0.8 * mid[bins], ink).astype(np.float32)


def render(mode, ink, pal, accent="Slate blue"):
    lab = {k: to_lab(v) for k, v in pal.items()}
    subject = ink > 0.2
    if not subject.any():
        sys.exit("nothing above the paper: is the mode right?")
    ink = rank(ink, subject)

    keys = [(0.20, "Window"), (0.28, "Comment"), (0.34, "Comment"),
            (0.42, "Muted"), (0.50, "Muted"), (0.60, accent),
            (0.76, accent), (0.82, "Ember"), (0.88, "Ember"), (0.95, "Text")]
    out = np.broadcast_to(lab["Window"], (H, W, 3)).copy()
    for (a, ca), (b, cb) in zip(keys, keys[1:]):
        m = ink > a
        w = smooth((ink[m] - a) / (b - a))[:, None]
        out[m] = lab[ca] + (lab[cb] - lab[ca]) * w
    return from_lab(out.reshape(-1, 3)).reshape(H, W, 3)


def check(img, pal, path):
    edge = [img[0, 0], img[0, -1], img[-1, 0], img[-1, -1]]
    if any((c != pal["Window"]).any() for c in edge):
        sys.exit(f"{path}: a corner is off the window colour")


def main(argv):
    v1 = "--v1" in argv
    argv = [a for a in argv if a != "--v1"]
    accent = "Slate blue"
    if "--accent" in argv:
        i = argv.index("--accent")
        accent = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) != 3 or argv[0] not in ("night", "day") or accent not in ACCENTS:
        sys.exit(__doc__.split("\n\n")[1] + "\n\naccent: " + ", ".join(ACCENTS))
    mode, src, out = argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pal = palette(root)
    ink = (ink_from_v1 if v1 else ink_from_grey)(mode, src)
    img = render(mode, ink, pal, accent)
    check(img, pal, out)
    Image.fromarray(img).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
