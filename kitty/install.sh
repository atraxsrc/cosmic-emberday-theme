#!/usr/bin/env bash
# Installs the EmberDay kitty colour scheme into ~/.config/kitty/themes/
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/kitty/themes
mkdir -p "$dest"
[ -f "$dest/EmberDay.conf" ] && cp "$dest/EmberDay.conf" "$dest/EmberDay.conf.bak"
cp "$dir/EmberDay.conf" "$dest/"
echo "Done. Add to ~/.config/kitty/kitty.conf:  include themes/EmberDay.conf"
echo "then reload kitty (Ctrl+Shift+F5)."
