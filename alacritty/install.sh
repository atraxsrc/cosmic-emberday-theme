#!/usr/bin/env bash
# Installs the EmberDay Alacritty colour scheme into ~/.config/alacritty/themes/
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/alacritty/themes
mkdir -p "$dest"
[ -f "$dest/emberday.toml" ] && cp "$dest/emberday.toml" "$dest/emberday.toml.bak"
cp "$dir/emberday.toml" "$dest/"
echo "Done. Add to ~/.config/alacritty/alacritty.toml:"
echo '  [general]'
echo '  import = ["~/.config/alacritty/themes/emberday.toml"]'
