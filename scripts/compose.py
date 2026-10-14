#!/usr/bin/env python3
"""Draw the Ember Day wallpapers: flat screen-print shapes on stone paper.

    python3 scripts/compose.py              # all four into backgrounds/
    python3 scripts/compose.py ridges tide  # just these

Ember Day is warm stone, ink and one ember accent, so every piece is the
window colour as paper, ink and the neutrals for the drawing, ember used once
(a sun, a route) and at most a couple of the calm colours. Filled shapes carry
a faint ink grain, as if printed; lines stay clean. Colours come from
backgrounds/emberday.gpl, and every piece is seeded, so a rerun gives the same
file.

    ridges    five layers of hills fading into the haze under an ember sun
    orbits    an astronomy chart: fine orbits round an ember sun, six planets
    contours  a topographic map with a lake and a dotted ember route
    tide      an ember sun setting over line-drawn waves, one small boat
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wallpaper import H, W, palette  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YS, XS = np.mgrid[0:H, 0:W].astype(np.float32)


class Canvas:
    def __init__(self, pal, seed):
        self.pal = pal
        self.img = np.broadcast_to(pal["Window"], (H, W, 3)).astype(np.float32).copy()
        self.rng = np.random.default_rng(seed)
        # ink grain: 2x2 specks where the paper shows through a filled shape
        g = self.rng.random((H // 2, W // 2)) > 0.88
        self.grain = np.repeat(np.repeat(g, 2, 0), 2, 1).astype(np.float32)

    def paint(self, cov, colour, grain=False, box=None):
        """Lay colour over the canvas with coverage cov (0-1), optionally only
        inside box = (y0, y1, x0, x1), the window cov was computed for."""
        y0, y1, x0, x1 = box or (0, H, 0, W)
        if grain:
            cov = cov * (1 - 0.3 * self.grain[y0:y1, x0:x1])
        c = cov[..., None]
        region = self.img[y0:y1, x0:x1]
        region += (self.pal[colour] - region) * c

    def disc(self, cx, cy, r, colour, grain=False):
        y0, y1 = max(int(cy - r - 2), 0), min(int(cy + r + 3), H)
        x0, x1 = max(int(cx - r - 2), 0), min(int(cx + r + 3), W)
        if y0 >= y1 or x0 >= x1:
            return
        d = np.hypot(XS[y0:y1, x0:x1] - cx, YS[y0:y1, x0:x1] - cy) - r
        self.paint(np.clip(0.5 - d, 0, 1), colour, grain, (y0, y1, x0, x1))

    def ring(self, cx, cy, r, width, colour):
        y0, y1 = max(int(cy - r - width - 2), 0), min(int(cy + r + width + 3), H)
        x0, x1 = max(int(cx - r - width - 2), 0), min(int(cx + r + width + 3), W)
        d = np.abs(np.hypot(XS[y0:y1, x0:x1] - cx, YS[y0:y1, x0:x1] - cy) - r) - width / 2
        self.paint(np.clip(0.5 - d, 0, 1), colour, box=(y0, y1, x0, x1))

    def capsule(self, x0, x1, y, h, colour, grain=False):
        """A long rounded bar, the cloud stroke of a print."""
        r = h / 2
        dx = np.maximum(np.maximum(x0 + r - XS, XS - (x1 - r)), 0)
        d = np.hypot(dx, YS - y) - r
        self.paint(np.clip(0.5 - d, 0, 1), colour, grain)

    def save(self, name):
        out = os.path.join(ROOT, "backgrounds", f"emberday-{name}.png")
        Image.fromarray(np.rint(self.img).clip(0, 255).astype(np.uint8)).save(out, optimize=True)
        print(out)


def wave1d(rng, x, base, amp, octaves=5, sharp=0.0):
    """A ridge line: summed sines with random phases, halving each octave;
    sharp > 0 folds them into peaks."""
    y = np.zeros_like(x)
    a, f = 1.0, 1.4 / W
    for _ in range(octaves):
        s = np.sin(2 * np.pi * f * x + rng.uniform(0, 2 * np.pi))
        y += a * ((1 - sharp) * s + sharp * (1 - 2 * np.abs(s)))
        a, f = a * 0.45, f * 2.1
    return base + amp * y / 1.9


def ridges(pal):
    cv = Canvas(pal, 11)
    cv.disc(0.66 * W, 0.34 * H, 0.12 * H, "Ember", grain=True)
    cv.capsule(0.50 * W, 0.84 * W, 0.37 * H, 20, "Window")
    cv.capsule(0.55 * W, 0.78 * W, 0.405 * H, 13, "Window")
    cv.capsule(0.10 * W, 0.34 * W, 0.24 * H, 16, "Container", grain=True)
    cv.capsule(0.18 * W, 0.42 * W, 0.27 * H, 10, "Container", grain=True)
    x = np.arange(W, dtype=np.float32)
    layers = [(0.54, 0.11, 0.45, "Pane"), (0.61, 0.10, 0.35, "Comment"),
              (0.70, 0.07, 0.25, "Muted"), (0.79, 0.05, 0.15, "Moss"),
              (0.89, 0.04, 0.05, "Text")]
    for base, amp, sharp, colour in layers:
        top = wave1d(cv.rng, x, base * H, amp * H, sharp=sharp)
        slope = np.sqrt(1 + np.gradient(top) ** 2)
        cv.paint(np.clip(0.5 + (YS - top[None, :]) / slope[None, :], 0, 1), colour, grain=True)
    for bx, by, s in [(0.40, 0.30, 1.0), (0.43, 0.27, 0.8), (0.38, 0.26, 0.7)]:
        for side in (-1, 1):  # two short strokes, a bird
            cx, cy = bx * W + side * 16 * s, by * H + 6 * s
            d = np.abs(np.hypot(XS - cx - side * 4 * s, YS - cy - 20 * s) - 22 * s) - 2.2
            on = (YS < cy + 4 * s) & (np.abs(XS - cx) < 18 * s)
            cv.paint(np.where(on, np.clip(0.5 - d, 0, 1), 0), "Text")
    cv.save("ridges")


def ellipse_stroke(cx, cy, rx, ry, rot, width):
    c, s = np.cos(rot), np.sin(rot)
    u = (XS - cx) * c + (YS - cy) * s
    v = -(XS - cx) * s + (YS - cy) * c
    q = np.sqrt((u / rx) ** 2 + (v / ry) ** 2) + 1e-6
    g = np.sqrt((u / rx ** 2) ** 2 + (v / ry ** 2) ** 2) / q + 1e-9
    return np.clip(0.5 - (np.abs(q - 1) / g - width / 2), 0, 1)


def orbits(pal):
    cv = Canvas(pal, 23)
    grid = np.minimum(np.abs((XS + 120) % 240 - 120), np.abs((YS + 60) % 240 - 120))
    cv.paint(np.clip(1.5 - grid, 0, 1), "Container")
    for _ in range(260):
        x, y = cv.rng.uniform(0, W), cv.rng.uniform(0, H)
        cv.disc(x, y, cv.rng.choice([1.6, 2.2, 3.2]), cv.rng.choice(["Comment", "Muted"]))
    sx, sy, rot = 0.34 * W, 0.55 * H, np.deg2rad(-9)
    radii = [0.12, 0.19, 0.27, 0.37, 0.49, 0.62]
    for i, r in enumerate(radii):
        cv.paint(ellipse_stroke(sx, sy, r * W, 0.34 * r * W, rot, 3.0 if i % 2 else 2.0),
                 "Muted" if i == 3 else "Comment")
    cv.disc(sx, sy, 0.14 * H, "Container")
    cv.ring(sx, sy, 0.11 * H, 2.5, "Comment")
    cv.disc(sx, sy, 0.08 * H, "Ember", grain=True)
    planets = [(0.12, 300, 22, "Slate blue"), (0.19, 40, 30, "Moss"), (0.27, 240, 44, "Amber"),
               (0.37, 330, 26, "Brick"), (0.49, 25, 36, "Heather"), (0.62, 350, 24, "Verdigris")]
    for r, ang, size, colour in planets:
        a = np.deg2rad(ang)
        u, v = r * W * np.cos(a), 0.34 * r * W * np.sin(a)
        px = sx + u * np.cos(rot) - v * np.sin(rot)
        py = sy + u * np.sin(rot) + v * np.cos(rot)
        cv.disc(px, py, size + 10, "Window")
        cv.disc(px, py, size, colour, grain=True)
        if colour == "Amber":
            cv.paint(ellipse_stroke(px, py, size * 2.1, size * 0.62, np.deg2rad(-20), 3.0), "Text")
            cv.disc(px, py - size * 0.25, size * 0.98, colour, grain=True)
    cv.save("orbits")


def field(rng, n=14):
    """A smooth height field: summed plane waves in random directions."""
    h = np.zeros((H, W), np.float32)
    for i in range(n):
        th = rng.uniform(0, np.pi)
        k = 2 * np.pi * rng.uniform(0.6, 2.4) / W
        h += np.cos(k * (XS * np.cos(th) + YS * np.sin(th)) + rng.uniform(0, 2 * np.pi)) / (1 + 0.15 * i)
    return (h - h.min()) / (h.max() - h.min())


def contours(pal):
    cv = Canvas(pal, 5)
    h = field(cv.rng)
    lake = h < 0.17
    edge = np.clip(0.5 + (0.17 - h) / (np.hypot(*np.gradient(h)) + 1e-9), 0, 1)
    cv.paint(edge, "Pane")
    hatch = (np.abs((YS % 22) - 11) < 1.6).astype(np.float32)
    cv.paint(hatch * lake * (h < 0.15), "Container")
    gy, gx = np.gradient(h)
    grad = np.hypot(gx, gy) + 1e-9
    for step, width, colour in [(0.025, 2.0, "Comment"), (0.125, 3.6, "Muted")]:
        t = h / step
        d = np.abs(t - np.round(t)) * step / grad
        cv.paint(np.clip(0.5 - (d - width / 2), 0, 1) * (h > 0.17), colour)
    cv.paint(np.clip(0.5 - (np.abs(h - 0.17) / grad - 1.6), 0, 1), "Slate blue")
    # the route: a smooth curve through a few points, drawn as ember dots
    pts = np.array([[0.08, 0.78], [0.22, 0.62], [0.36, 0.70], [0.50, 0.48],
                    [0.63, 0.38], [0.76, 0.46], [0.88, 0.26]]) * [W, H]
    path = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for t in np.linspace(0, 1, 400, endpoint=False):
            path.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                               + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    path = np.array(path)
    run = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(path, axis=0).T))])
    for s in np.arange(30, run[-1] - 30, 30):
        x, y = np.interp(s, run, path[:, 0]), np.interp(s, run, path[:, 1])
        cv.disc(x, y, 6.5, "Ember")
    (ax, ay), (bx, by) = pts[0], pts[-1]
    cv.disc(ax, ay, 26, "Window")
    cv.ring(ax, ay, 18, 6, "Ember")
    cv.disc(bx, by, 30, "Ember", grain=True)
    cv.ring(bx, by, 40, 3, "Text")
    cv.save("contours")


def tide(pal):
    cv = Canvas(pal, 17)
    horizon, sx, r = 0.60 * H, 0.5 * W, 0.21 * H
    d = np.hypot(XS - sx, YS - horizon) - r
    cv.paint(np.clip(0.5 - d, 0, 1) * np.clip(horizon - YS + 0.5, 0, 1), "Ember", grain=True)
    for y, hgt in [(0.50, 12), (0.535, 18), (0.565, 26)]:  # the sun sinks behind bars of paper
        cv.capsule(sx - 1.2 * r, sx + 1.2 * r, y * H, hgt, "Window")
    cv.capsule(0.08 * W, 0.30 * W, 0.20 * H, 14, "Container", grain=True)
    cv.capsule(0.15 * W, 0.38 * W, 0.235 * H, 9, "Container", grain=True)
    cv.capsule(0.66 * W, 0.93 * W, 0.15 * H, 12, "Container", grain=True)
    cv.paint(np.clip(1.6 - np.abs(YS - horizon), 0, 1), "Text")
    y, gap, n = horizon + 22, 18.0, 0
    while y < H + 40:
        depth = (y - horizon) / (H - horizon)
        width = 1.6 + 3.4 * depth
        wy = y + (5 + 9 * depth) * np.sin(XS[0] / (90 + 160 * depth) + cv.rng.uniform(0, 6.3))
        line = np.clip(0.5 - (np.abs(YS - wy[None, :]) - width / 2), 0, 1)
        dash = (np.sin(XS / (60 + 120 * depth) + cv.rng.uniform(0, 6.3)) > -0.55).astype(np.float32)
        glow = np.abs(XS - sx) < r * (1.0 - 0.75 * depth) * (0.75 + 0.25 * np.sin(n * 1.7))
        cv.paint(line * dash * ~glow, "Slate blue" if n % 3 else "Muted")
        cv.paint(line * glow, "Ember")
        y, gap, n = y + gap, gap * 1.07, n + 1
    bx, by = 0.30 * W, horizon + 0.06 * H  # the boat: hull and sail
    hull = (YS > by - 10) & (YS < by + 12) & (np.abs(XS - bx) < 70 - 0.9 * (YS - by + 10))
    sail = (YS < by - 14) & (YS > by - 140) & (XS > bx - 6) & (XS < bx + 6 + 0.55 * (YS - by + 140))
    mast = (np.abs(XS - bx) < 3) & (YS > by - 150) & (YS < by - 8)
    cv.paint((hull | sail | mast).astype(np.float32), "Text")
    cv.save("tide")


PIECES = {"ridges": ridges, "orbits": orbits, "contours": contours, "tide": tide}

if __name__ == "__main__":
    names = sys.argv[1:] or list(PIECES)
    bad = [n for n in names if n not in PIECES]
    if bad:
        sys.exit(__doc__.split("\n\n")[1] + "\n\npieces: " + ", ".join(PIECES))
    pal = palette(ROOT)
    for n in names:
        PIECES[n](pal)
