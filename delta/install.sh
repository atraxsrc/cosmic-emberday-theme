#!/usr/bin/env bash
# Installs the EmberDay delta config into ~/.config/delta/. It does not edit
# ~/.gitconfig: add the [include] it prints.
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
dest=~/.config/delta
mkdir -p "$dest"
[ -f "$dest/emberday.gitconfig" ] && cp "$dest/emberday.gitconfig" "$dest/emberday.gitconfig.bak"
cp "$dir/emberday.gitconfig" "$dest/"
if [ -f ~/.gitconfig ] && grep -qF "delta/emberday.gitconfig" ~/.gitconfig; then
    echo "Done. ~/.gitconfig already includes it."
else
    echo "Done. Add to ~/.gitconfig:"
    echo "  [include]"
    echo "      path = ~/.config/delta/emberday.gitconfig"
fi
echo "Needs the bat EmberDay theme for the code colours: ./bat/install.sh"
