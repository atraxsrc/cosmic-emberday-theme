#!/usr/bin/env bash
# Render one Ember wallpaper from a source image with ImageMagick 6.
#
#   ./scripts/wallpaper.sh night ../cool-wallpapers/omarchy/the-greek/the-greek-bg1-3840x2160.jpg backgrounds/ember-eagle.png
#   ./scripts/wallpaper.sh day   ../cool-wallpapers/omarchy/the-greek/the-greek-bg1-3840x2160.jpg backgrounds/emberday-eagle.png
#
# The source is converted to grey, inverted when its mean luminance is above
# 0.5 for night (ink-on-paper sources) or below 0.5 for day (dark sources),
# then mapped through a 256-row colour lookup built from stacked gradients:
#   night: #15171C > #2A2F38 > #7C8290 > #E8713A > #F1D9C8  (ember on highlights only)
#   day:   #2B2E36 > #6B6F78 > #A4441A > #D4CFC6 > #E9E6DF
# The window end of the lookup is a flat band (night: the darkest 19 percent,
# day: the lightest 20 percent) so a source background that is not pure
# black or white still lands exactly on the window colour.
# Output is cover-cropped and centred at 3840x2160, alpha dropped.
set -euo pipefail

mode="${1:-}"; src="${2:-}"; out="${3:-}"
[[ "$mode" == night || "$mode" == day ]] || { echo "usage: $0 night|day SOURCE OUT"; exit 1; }
[[ -f "$src" ]] || { echo "no source at $src"; exit 1; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
if [[ "$mode" == night ]]; then
  convert -size 1x48 xc:'#15171C' -size 1x42 gradient:'#15171C-#2A2F38' -size 1x70 gradient:'#2A2F38-#7C8290' -size 1x60 gradient:'#7C8290-#E8713A' -size 1x36 gradient:'#E8713A-#F1D9C8' -append "$tmp/clut.png"
else
  convert -size 1x100 gradient:'#2B2E36-#6B6F78' -size 1x50 gradient:'#6B6F78-#A4441A' -size 1x40 gradient:'#A4441A-#D4CFC6' -size 1x15 gradient:'#D4CFC6-#E9E6DF' -size 1x51 xc:'#E9E6DF' -append "$tmp/clut.png"
fi

mean="$(convert "$src" -resize 400x400 -colorspace Gray -format '%[fx:mean]' info:)"
neg=()
if [[ "$mode" == night ]]; then
  (( $(echo "$mean > 0.5" | bc) )) && neg=(-negate)
else
  (( $(echo "$mean < 0.5" | bc) )) && neg=(-negate)
fi

mkdir -p "$(dirname "$out")"
convert "$src" -resize 3840x2160^ -gravity center -extent 3840x2160 -colorspace Gray "${neg[@]}" "$tmp/clut.png" -clut -alpha off -strip "$out"
echo "$out  (mean $mean, ${neg[*]:-as is})"
