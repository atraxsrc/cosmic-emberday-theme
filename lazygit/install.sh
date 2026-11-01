#!/usr/bin/env bash
# Installs the EmberDay lazygit colours beside your own config.yml
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/lazygit
mkdir -p "$dest"
[ -f "$dest/emberday.yml" ] && cp "$dest/emberday.yml" "$dest/emberday.yml.bak"
cp "$dir/emberday.yml" "$dest/"
echo "Done. zsh/emberday.zsh points LG_CONFIG_FILE at config.yml plus emberday.yml; without it:"
echo "  export LG_CONFIG_FILE=\"\$HOME/.config/lazygit/config.yml,\$HOME/.config/lazygit/emberday.yml\""
