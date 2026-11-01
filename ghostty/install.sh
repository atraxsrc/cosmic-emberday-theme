#!/usr/bin/env bash
# Installs the EmberDay Ghostty theme into ~/.config/ghostty/themes/
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/ghostty/themes
mkdir -p "$dest"
[ -f "$dest/EmberDay" ] && cp "$dest/EmberDay" "$dest/EmberDay.bak"
cp "$dir/EmberDay" "$dest/"
echo "Done. Add to ~/.config/ghostty/config:  theme = EmberDay"
echo "(or  theme = dark:Ember,light:EmberDay  to follow COSMIC's toggle), then reload: Ctrl+Shift+,"
