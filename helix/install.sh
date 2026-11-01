#!/usr/bin/env bash
# Installs the EmberDay Helix theme into ~/.config/helix/themes/
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/helix/themes
mkdir -p "$dest"
[ -f "$dest/emberday.toml" ] && cp "$dest/emberday.toml" "$dest/emberday.toml.bak"
cp "$dir/emberday.toml" "$dest/"
echo 'Done. Add to ~/.config/helix/config.toml:  theme = "emberday"'
