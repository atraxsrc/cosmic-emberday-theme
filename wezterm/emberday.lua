-- EmberDay for WezTerm, part of cosmic-emberday-theme (MIT).
-- Colours follow the COSMIC Terminal scheme (cosmic-term/).
--
-- Install: ./wezterm/install.sh puts this in ~/.config/wezterm/, then in
-- ~/.config/wezterm/wezterm.lua:
--   config.colors = require("emberday")
-- To follow COSMIC's Dark / Light toggle with the Ember half installed too:
--   local dark = (wezterm.gui and wezterm.gui.get_appearance() or "Dark"):find("Dark")
--   config.colors = require(dark and "ember" or "emberday")

return {
  foreground = "#2B2E36",
  background = "#DDD9D1",

  cursor_bg = "#A4441A",
  cursor_fg = "#DDD9D1",
  cursor_border = "#A4441A",
  compose_cursor = "#8A5E12",

  selection_bg = "#BBB9B2",
  selection_fg = "none",

  scrollbar_thumb = "#BBB9B2",
  split = "#BBB9B2",

  -- black, red, green, yellow, blue, magenta, cyan, white
  ansi = { "#2B2E36", "#9E3A3A", "#4C6B45", "#8A5E12", "#2F5C8A", "#6E4E8C", "#2E6E6A", "#6B6F78" },
  brights = { "#25272E", "#863131", "#415B3B", "#75500F", "#284E75", "#5E4277", "#275E5A", "#5B5E66" },

  copy_mode_active_highlight_bg = { Color = "#A4441A" },
  copy_mode_active_highlight_fg = { Color = "#E9E6DF" },
  copy_mode_inactive_highlight_bg = { Color = "#8A5E12" },
  copy_mode_inactive_highlight_fg = { Color = "#DDD9D1" },

  quick_select_label_bg = { Color = "#8A5E12" },
  quick_select_label_fg = { Color = "#DDD9D1" },
  quick_select_match_bg = { Color = "#8A5E12" },
  quick_select_match_fg = { Color = "#DDD9D1" },

  tab_bar = {
    background = "#DDD9D1",
    active_tab = { bg_color = "#A4441A", fg_color = "#E9E6DF", intensity = "Bold" },
    inactive_tab = { bg_color = "#E2DED6", fg_color = "#5C5F67" },
    inactive_tab_hover = { bg_color = "#DDD9D1", fg_color = "#2B2E36" },
    new_tab = { bg_color = "#DDD9D1", fg_color = "#5C5F67" },
    new_tab_hover = { bg_color = "#DDD9D1", fg_color = "#9F4219" },
  },
}
