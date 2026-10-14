#!/usr/bin/env python3
"""Recolour a Catppuccin Mocha wallpaper into this repo's palette.

    python3 scripts/mocha.py night SOURCE OUT.png
    python3 scripts/mocha.py day   SOURCE OUT.png

SOURCE is a wallpaper already drawn in Catppuccin Mocha, such as one from
github.com/atraxsrc/catppuccin-mocha-walls. Each of the 26 Mocha colours has a
role here, and every pixel moves by the inverse-distance blend (in OKLab) of
the moves its nearest Mocha colours make, so texture and soft edges survive
and a pixel sitting on a Mocha colour lands exactly on its role:

    mantle, crust      window (the paper)
    base, surface0     pane, container
    surface1-text      comment, muted, text, with the steps between
    maroon, peach      ember          flamingo, rosewater  ember toward text
    red                brick          yellow       amber
    green              moss           teal, sky    verdigris
    blue, sapphire     slate blue     mauve, pink, lavender  heather

The warm Mocha colours all go to the ember family, so a pink-to-yellow sunset
stays one glow instead of breaking into bands. The pictures worth recolouring
are the ones that are mostly night with a small glow: the blue-black does the
work and ember stays small and loud, as the palette asks.

night keeps Mocha's light order. day turns the neutrals over, so the dark
paper becomes the stone window and the lightest strokes become ink, and the
accents take Ember Day's darker values.

The result is cover-cropped to 3840x2160 and gets the palette strip of
scripts/wallpaper.py, so every palette colour is present as its exact hex.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wallpaper import H, W, check, from_lab, palette, strip, to_lab  # noqa: E402

MOCHA = {
    "rosewater": "f5e0dc", "flamingo": "f2cdcd", "pink": "f5c2e7", "mauve": "cba6f7",
    "red": "f38ba8", "maroon": "eba0ac", "peach": "fab387", "yellow": "f9e2af",
    "green": "a6e3a1", "teal": "94e2d5", "sky": "89dceb", "sapphire": "74c7ec",
    "blue": "89b4fa", "lavender": "b4befe", "text": "cdd6f4", "subtext1": "bac2de",
    "subtext0": "a6adc8", "overlay2": "9399b2", "overlay1": "7f849c", "overlay0": "6c7086",
    "surface2": "585b70", "surface1": "45475a", "surface0": "313244", "base": "1e1e2e",
    "mantle": "181825", "crust": "11111b",
}


def roles(lab, mode):
    """Target OKLab colour for each Mocha name: a palette role, or a step
    between two roles written (a, b, t)."""
    mix = lambda a, b, t: lab[a] + (lab[b] - lab[a]) * t  # noqa: E731
    beyond = mix("Window", "Pane", -1.0)  # one step past the window, for crust
    near, far = sorted(["Pane", "Container"], key=lambda k: abs(lab[k][0] - lab["Window"][0]))
    return {
        "crust": beyond, "mantle": lab["Window"], "base": lab[near], "surface0": lab[far],
        "surface1": mix(far, "Comment", 0.5), "surface2": lab["Comment"],
        "overlay0": mix("Comment", "Muted", 0.5), "overlay1": lab["Muted"],
        "overlay2": mix("Muted", "Text", 0.25), "subtext0": mix("Muted", "Text", 0.5),
        "subtext1": mix("Muted", "Text", 0.75), "text": lab["Text"],
        "maroon": lab["Ember"], "peach": lab["Ember"], "red": lab["Brick"],
        "yellow": lab["Amber"], "green": lab["Moss"], "teal": lab["Verdigris"],
        "sky": lab["Verdigris"], "blue": lab["Slate blue"], "sapphire": lab["Slate blue"],
        "mauve": lab["Heather"], "pink": lab["Heather"], "lavender": mix("Heather", "Text", 0.3),
        "flamingo": mix("Ember", "Text", 0.35), "rosewater": mix("Ember", "Text", 0.65),
    }


def recolour(img, pal, mode, power=4.0):
    lab = {k: to_lab(v) for k, v in pal.items()}
    tgt = roles(lab, mode)
    src = np.array([to_lab(np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)) for h in MOCHA.values()])
    move = np.array([tgt[k] for k in MOCHA]) - src

    flat = img.reshape(-1, 3)
    keys = (flat[:, 0].astype(np.int32) << 16) | (flat[:, 1].astype(np.int32) << 8) | flat[:, 2]
    uniq, inv = np.unique(keys, return_inverse=True)
    ucol = np.stack([uniq >> 16, (uniq >> 8) & 255, uniq & 255], 1).astype(np.float64)
    out = np.empty((len(ucol), 3))
    for i in range(0, len(ucol), 200000):
        c = to_lab(ucol[i:i + 200000])
        d = np.sqrt(((c[:, None, :] - src[None]) ** 2).sum(-1))
        w = 1 / (d ** power + 1e-12)
        out[i:i + 200000] = c + (w[..., None] * move[None]).sum(1) / w.sum(1, keepdims=True)
    return from_lab(out)[inv].reshape(img.shape)


def cover(path):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return np.asarray(im.crop((x, y, x + W, y + H)))


def main(argv):
    if len(argv) != 3 or argv[0] not in ("night", "day"):
        sys.exit(__doc__.split("\n\n")[1])
    mode, src, out = argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pal = palette(root)
    img = recolour(cover(src), pal, mode)
    strip(img, pal)
    check(img, pal, out, corners=False)  # a painting keeps its own edges
    Image.fromarray(img).save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
