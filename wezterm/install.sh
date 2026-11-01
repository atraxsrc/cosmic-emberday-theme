#!/usr/bin/env bash
# Installs the EmberDay WezTerm colour module into ~/.config/wezterm/
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/wezterm
mkdir -p "$dest"
[ -f "$dest/emberday.lua" ] && cp "$dest/emberday.lua" "$dest/emberday.lua.bak"
cp "$dir/emberday.lua" "$dest/"
echo 'Done. Add to ~/.config/wezterm/wezterm.lua:  config.colors = require("emberday")'
