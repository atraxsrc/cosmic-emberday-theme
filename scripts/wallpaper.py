#!/usr/bin/env python3
"""Recolour one wallpaper with every colour of the repo palette.

    python3 scripts/wallpaper.py night GREY.png OUT.png
    python3 scripts/wallpaper.py day   GREY.png OUT.png
    python3 scripts/wallpaper.py night --v1 backgrounds/ember-eagle.png OUT.png

GREY is the cover-cropped grey render that scripts/wallpaper.sh prepares (light
subject on dark for night, dark subject on light for day). --v1 instead reads
a wallpaper made by the first, two-tone lookup and recovers its grey levels, so
the shipped wallpapers can be redone without the cool-wallpapers sources.

The palette is read from backgrounds/*.gpl. Each pixel gets an ink level, 0 on
the paper and 1 on the strongest line, and runs along one ramp of roles:

    ink  0.00-0.20  window, flat, so the paper lands exactly on the window
         0.20-0.46  comment, then muted (shadows and fine lines)
         0.46-0.80  one of the seven colours (ember, moss, amber, brick,
                    slate blue, heather, verdigris), held flat
         0.80-1.00  text (fog by night, ink by day) on the strongest lines

Which of the seven a pixel takes depends on where it sits: the subject is
swept on a diagonal and split into seven bands of equal ink, so each colour
covers about a seventh of the subject. Behind the subject sits a stepped disc
in pane and container, kept clear of the corners so they stay on the window.
Blends between roles are mixed in OKLab; every role holds a flat band, so
each palette colour is present as its exact hex.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

W, H = 3840, 2160
HUES = ["Slate blue", "Verdigris", "Moss", "Amber", "Ember", "Brick", "Heather"]
SWEEP = np.deg2rad(28)  # top left to bottom right

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


def densest(mask, step=16):
    """Centroid of the mask weighted by the square of its local density (a box
    a sixth of the height wide), so solid shapes count and thin lines barely do."""
    h, w = H // step, W // step
    small = mask[:h * step, :w * step].reshape(h, step, w, step).mean((1, 3))
    k = H // 6 // step
    c = np.pad(small, ((k // 2 + 1, k - k // 2), (k // 2 + 1, k - k // 2))).cumsum(0).cumsum(1)
    box = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k])[:h, :w] / k ** 2
    wt = small * box ** 2
    yy, xx = np.mgrid[0:h, 0:w]
    return ((xx * wt).sum() / wt.sum() + 0.5) * step, ((yy * wt).sum() / wt.sum() + 0.5) * step


def rank(ink, subject):
    """Spread the subject's ink evenly over 0.2-1 by its own distribution (ties
    take their middle rank), so a faint render and a bold one both run the whole
    ramp and every role lands on part of the subject."""
    bins = np.clip((ink * 4095).astype(np.int32), 0, 4095)
    n = np.bincount(bins[subject], minlength=4096).astype(np.float64)
    mid = (np.cumsum(n) - n / 2) / n.sum()
    return np.where(subject, 0.2 + 0.8 * mid[bins], ink).astype(np.float32)


def render(mode, ink, pal):
    lab = {k: to_lab(v) for k, v in pal.items()}
    window = lab["Window"]
    # outer disc is whichever of pane / container sits nearer the window
    near, far = sorted(["Pane", "Container"], key=lambda k: abs(lab[k][0] - window[0]))

    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    subject = ink > 0.2
    ink = rank(ink, subject)
    if not subject.any():
        sys.exit("nothing above the paper: is the mode right?")

    # stepped disc behind the subject: centred where the subject is densest
    # (so thin lines trailing off do not pull it away), wide enough for most
    # of it, its rim kept 120 px inside every edge where the room allows
    cx, cy = densest(subject)
    dist = np.hypot(xs - cx, ys - cy)
    r = 1.15 * np.percentile(dist[subject], 70)
    r = min(r, cx - 120, W - 120 - cx, cy - 120, H - 120 - cy, 0.46 * H)
    r = max(r, 0.16 * H)
    outer = np.clip(r - dist + 0.5, 0, 1)[..., None]
    inner = np.clip(0.72 * r - dist + 0.5, 0, 1)[..., None]
    base = window + (lab[near] - window) * outer
    base = base + (lab[far] - base) * inner

    # colour sweep: equal-ink bands of the seven colours along a diagonal
    proj = xs * np.cos(SWEEP) + ys * np.sin(SWEEP)
    hot = (ink > 0.48) & (ink < 0.84)
    pts = proj[hot] if hot.sum() > 1000 else proj[subject]
    q = np.quantile(pts, np.linspace(0, 1, 513))
    q = np.maximum.accumulate(q + np.arange(513) * 1e-4)
    t = np.interp(proj, q, np.linspace(0, 1, 513))
    s = np.clip(t * len(HUES) - 0.5, 0, len(HUES) - 1)
    i = np.minimum(s.astype(np.int32), len(HUES) - 2)
    f = smooth((s - i - 0.3) / 0.4)[..., None]
    hues = np.array([lab[k] for k in HUES])
    hue = hues[i] + (hues[i + 1] - hues[i]) * f

    keys = [(0.20, base), (0.26, lab["Comment"]), (0.31, lab["Comment"]),
            (0.37, lab["Muted"]), (0.42, lab["Muted"]), (0.48, hue),
            (0.84, hue), (0.92, lab["Text"])]
    out = np.broadcast_to(base, (H, W, 3)).copy()
    for (a, ca), (b, cb) in zip(keys, keys[1:]):
        m = ink > a
        w = smooth((ink[m] - a) / (b - a))[:, None]
        ca = ca[m] if np.ndim(ca) == 3 else ca
        cb = cb[m] if np.ndim(cb) == 3 else cb
        out[m] = ca + (cb - ca) * w
    return from_lab(out.reshape(-1, 3)).reshape(H, W, 3)


def check(img, pal, path):
    flat = img.reshape(-1, 3)
    missing = []
    for k, v in pal.items():
        n = int(np.all(flat == v.astype(np.uint8), axis=1).sum())
        if n < 500:
            missing.append(f"{k} ({n} px)")
    corners = [img[0, 0], img[0, -1], img[-1, 0], img[-1, -1]]
    if any((c != pal["Window"]).any() for c in corners):
        missing.append("window corners")
    if missing:
        sys.exit(f"{path}: short of " + ", ".join(missing))


def main(argv):
    v1 = "--v1" in argv
    argv = [a for a in argv if a != "--v1"]
    if len(argv) != 3 or argv[0] not in ("night", "day"):
        sys.exit(__doc__.split("\n\n")[1])
    mode, src, out = argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pal = palette(root)
    ink = (ink_from_v1 if v1 else ink_from_grey)(mode, src)
    img = render(mode, ink, pal)
    check(img, pal, out)
    Image.fromarray(img).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
