# Cosmic Ember / Cosmic Ember Day for Cursor

Colour themes for [Cursor](https://cursor.com) from the COSMIC
[Ember](https://github.com/atraxsrc/cosmic-ember-theme) rice and its light half
[Ember Day](https://github.com/atraxsrc/cosmic-emberday-theme): **Cosmic Ember** and **Cosmic Ember Day** in one
extension. It is a plain VS Code theme extension, so VS Code and VSCodium
take it too. The same folder ships in both repos.

## Install

```bash
./vscode/install.sh                # Cursor
./vscode/install.sh code codium    # VS Code / VSCodium instead
```

It packs this folder into `vscode/cosmic-ember-theme-<version>.vsix` and installs
that with the editor's CLI (`cursor --install-extension`), so the theme is
listed under Extensions and running the script again updates it. Then press
<kbd>Ctrl</kbd>+<kbd>K</kbd> <kbd>Ctrl</kbd>+<kbd>T</kbd> and pick **Cosmic Ember** or **Cosmic Ember Day**.

No CLI on the PATH (an AppImage, say): the script still builds the `.vsix`;
install it from Extensions → `...` → **Install from VSIX**.

## Follow COSMIC's Dark / Light toggle

COSMIC tells apps which mode is on through its desktop portal. With these
lines in Cursor's `settings.json` (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> →
**Preferences: Open User Settings (JSON)**), Cursor switches between the two
themes along with the desktop:

```jsonc
"window.autoDetectColorScheme": true,
"workbench.preferredDarkColorTheme": "Cosmic Ember",
"workbench.preferredLightColorTheme": "Cosmic Ember Day"
```

## What it colours

Code is coloured the way Neovim is in the rice (`nvim/colors/*.lua`):

| Role | Ember | Ember Day |
|------|-------|-----------|
| Keywords, tags | ![#B08BC4](https://placehold.co/12x12/B08BC4/B08BC4.png) `#B08BC4` | ![#6E4E8C](https://placehold.co/12x12/6E4E8C/6E4E8C.png) `#6E4E8C` |
| Functions, tag attributes | ![#7FA3C7](https://placehold.co/12x12/7FA3C7/7FA3C7.png) `#7FA3C7` | ![#2F5C8A](https://placehold.co/12x12/2F5C8A/2F5C8A.png) `#2F5C8A` |
| Strings | ![#8FB58A](https://placehold.co/12x12/8FB58A/8FB58A.png) `#8FB58A` | ![#496742](https://placehold.co/12x12/496742/496742.png) `#496742` |
| Numbers, constants | ![#D9A441](https://placehold.co/12x12/D9A441/D9A441.png) `#D9A441` | ![#8A5E12](https://placehold.co/12x12/8A5E12/8A5E12.png) `#8A5E12` |
| Types, classes, modules | ![#7FB7B3](https://placehold.co/12x12/7FB7B3/7FB7B3.png) `#7FB7B3` | ![#2E6E6A](https://placehold.co/12x12/2E6E6A/2E6E6A.png) `#2E6E6A` |
| Imports, macros, decorators, escapes, `this` / `self` | ![#E8713A](https://placehold.co/12x12/E8713A/E8713A.png) `#E8713A` | ![#A4441A](https://placehold.co/12x12/A4441A/A4441A.png) `#A4441A` |
| Parameters (italic) | ![#7C8290](https://placehold.co/12x12/7C8290/7C8290.png) `#7C8290` | ![#646770](https://placehold.co/12x12/646770/646770.png) `#646770` |
| Operators, punctuation | ![#7C8290](https://placehold.co/12x12/7C8290/7C8290.png) `#7C8290` | ![#646770](https://placehold.co/12x12/646770/646770.png) `#646770` |
| Comments (italic) | ![#5F6574](https://placehold.co/12x12/5F6574/5F6574.png) `#5F6574` | ![#7F838B](https://placehold.co/12x12/7F838B/7F838B.png) `#7F838B` |
| Accent | ![#E8713A](https://placehold.co/12x12/E8713A/E8713A.png) `#E8713A` | ![#9F4219](https://placehold.co/12x12/9F4219/9F4219.png) `#9F4219` |

The workbench takes the window colour of the rice's `cosmic/*.ron` for the
editor, side bars, panel, title and status bar, the container colours for
menus, hovers, inputs and the command palette, and the accent for the active
tab line, buttons, badges and the menu highlight. The integrated terminal uses
the rice's COSMIC Terminal scheme (`cosmic-term/`), so command output looks the
same as in COSMIC Terminal.

Cursor's own panels (Agent, chat, inline diffs) have no colour keys of their
own. Cursor builds them from standard ones, and the theme sets those: the
button colour is the agent's accent, the side bar and panel colours are its
surfaces, the diff colours are its accept / reject highlights, and the
terminal's `blue` slot colours its links.

## Contrast

Text is at least 4.5:1 on the window background and on menus and hovers,
comments and line numbers at least 3:1, checked with a script over the text
and background pairs the theme sets.
Where a Neovim colour falls short, it is darkened (light theme) or lightened
(dark theme) just far enough here:

- **Ember**: comments and line numbers `#5A6070` → `#5F6574`; secondary text (status bar, titles, descriptions) `#7C8290` → `#808693`.
- **Ember Day**: comments and line numbers `#8C9099` → `#7F838B`; operators, parameters and secondary labels `#6B6F78` → `#646770`; secondary text (status bar, titles, descriptions) `#646770` → `#5C5F67`; the accent `#A4441A` → `#9F4219`; strings `#4C6B45` → `#496742`; warnings and modified files `#8A5E12` → `#714D0F`; added files and success marks `#4C6B45` → `#415B3B`.

On the highlighted current line, code can dip slightly under 4.5:1 and
comments under 3:1.
