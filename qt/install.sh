#!/usr/bin/env bash
# Installs the EmberDay Qt colour scheme for qt5ct and qt6ct
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
for v in qt5ct qt6ct; do
    dest=~/.config/$v/colors
    mkdir -p "$dest"
    [ -f "$dest/EmberDay.conf" ] && cp "$dest/EmberDay.conf" "$dest/EmberDay.conf.bak"
    cp "$dir/EmberDay.conf" "$dest/"
    echo "  $v: colors/EmberDay.conf"
done
echo "Done. In qt5ct / qt6ct: Appearance -> Color scheme -> EmberDay, Palette: Custom -> Apply."
echo "Qt apps read it with QT_QPA_PLATFORMTHEME=qt6ct (or qt5ct) in the environment."
