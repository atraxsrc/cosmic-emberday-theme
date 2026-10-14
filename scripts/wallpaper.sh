#!/usr/bin/env bash
# Render one Ember wallpaper from a source image: ImageMagick 6 for the grey,
# scripts/wallpaper.py (Python 3, numpy, Pillow) for the colour.
#
#   ./scripts/wallpaper.sh night ../cool-wallpapers/omarchy/the-greek/the-greek-bg1-3840x2160.jpg backgrounds/ember-eagle.png
#   ./scripts/wallpaper.sh day   ../cool-wallpapers/omarchy/the-greek/the-greek-bg1-3840x2160.jpg backgrounds/emberday-eagle.png
#
# The source is cover-cropped and centred at 3840x2160, converted to 16-bit
# grey and inverted when its mean luminance is above 0.5 for night (ink-on-paper
# sources) or below 0.5 for day (dark sources). wallpaper.py then maps the grey
# onto backgrounds/*.gpl: window paper, comment and muted shadows, slate blue
# for the body, ember on the brightest strokes, text on the strongest lines.
# See its docstring.
set -euo pipefail

mode="${1:-}"; src="${2:-}"; out="${3:-}"
[[ "$mode" == night || "$mode" == day ]] || { echo "usage: $0 night|day SOURCE OUT"; exit 1; }
[[ -f "$src" ]] || { echo "no source at $src"; exit 1; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mean="$(convert "$src" -resize 400x400 -colorspace Gray -format '%[fx:mean]' info:)"
neg=()
if [[ "$mode" == night ]]; then
  (( $(echo "$mean > 0.5" | bc) )) && neg=(-negate)
else
  (( $(echo "$mean < 0.5" | bc) )) && neg=(-negate)
fi

mkdir -p "$(dirname "$out")"
convert "$src" -resize 3840x2160^ -gravity center -extent 3840x2160 -colorspace Gray "${neg[@]}" -alpha off -depth 16 "$tmp/grey.png"
python3 "$(dirname "$0")/wallpaper.py" "$mode" "$tmp/grey.png" "$out"
echo "$out  (mean $mean, ${neg[*]:-as is})"
