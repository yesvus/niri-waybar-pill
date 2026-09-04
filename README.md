# niri-waybar-pill 💊

A collection of minimal, compact, pill-styled window management solutions for the [Niri](https://github.com/niri-wm/niri) scrollable tiling window manager and [Waybar](https://github.com/Alexays/Waybar).

Designed for users who want borderless, CSD-free terminal windows without sacrificing window titles, quick window controls, or taskbar access.

---

## What's Included

### 1. Interactive Firefox-Style Tabs (`niri-tab-daemon.py` & `niri-tab-action.sh`) 🚀 *(Recommended)*
* **Seamless Firefox Pills:** Each window tab is rendered as a clean, unified pill with an integrated minimal close button (`✕`) centered at the right end with balanced margins.
* **Double-Click to Maximize (CSD Style):** Double-clicking any tab toggles `maximize-window-to-edges` (Niri's `Mod+M` equivalent), replicating classic desktop window titlebar behavior.
* **Direct Window Jumping:** Left-clicking the tab body focuses that specific window immediately (`niri msg action focus-window --id <ID>`).
* **Integrated Actions & Mouse Macros:** Left-clicking the close button (or right/middle-clicking the tab body) immediately closes that window (`niri msg action close-window --id <ID>`).
* **Clean Tooltips:** Hovering over tabs displays only the pure window title without shortcut clutter or ID noise.
* **Reserved Navigation Space (Zero Layout Jitter):** Fixed allocation for `‹` and `›` pagination and overflow fades ensures tabs never shift or jump horizontally when scrolling between windows.
* **Configurable Tooling (`~/.config/niri-tabs/config.json`):** Make the close button optional (ideal for mouse macro users), enable an optional enlarge/maximize button, configure slot limits, title lengths, and custom icons with hot reloading.
* **Smooth Easing Transitions:** Calibrated with `transition: all 150ms cubic-bezier(0.215, 0.61, 0.355, 1);` matching Niri's default `ease-out-cubic` curve.

### 2. Single-Module Workspace Taskbar (`niri-taskbar.py`)
* Lightweight single-span taskbar for minimal setups.
* Left-click toggles overview, scroll cycles windows.

### 3. Workspace Window Counter (`niri-wincount.py`)
* Event-driven radar daemon (`󱂬 <count>`) tracking how many windows are currently in your scrollable workspace strip.

---

## Configuration (`~/.config/niri-tabs/config.json`)

Configure your tab preferences at `~/.config/niri-tabs/config.json` (changes take effect automatically):

```json
{
  "max_slots": 6,
  "max_title_len": 8,
  "reserve_navigation": true,
  "show_close_button": true,
  "show_maximize_button": false,
  "close_icon": "✕",
  "maximize_icon": "□"
}
```

| Key | Type | Default | Description |
|---|---|---|---|
| `max_slots` | integer | `6` | Maximum visible tab slots in the bar. |
| `max_title_len` | integer | `8` | Maximum title length before smooth alpha fade begins. |
| `reserve_navigation` | boolean | `true` | Reserves space for `‹` and `›` arrows to prevent tab jitter when scrolling. |
| `show_close_button` | boolean | `true` | Show the integrated `✕` close button on each tab. |
| `show_maximize_button` | boolean | `false` | Show an optional `□` enlarge/maximize button on each tab. |
| `close_icon` | string | `"✕"` | Custom glyph or text for the close button. |
| `maximize_icon` | string | `"□"` | Custom glyph or text for the maximize button. |

---

## Quick Setup (Firefox-Style Tabs)

### 1. Copy Daemon & Action Handler
```bash
cp niri-tab-daemon.py niri-tab-action.sh ~/.config/waybar/
chmod +x ~/.config/waybar/niri-tab-daemon.py ~/.config/waybar/niri-tab-action.sh
```

### 2. Optional: Setup Configuration File
```bash
mkdir -p ~/.config/niri-tabs
cp config.json.example ~/.config/niri-tabs/config.json
```

### 3. Configure Waybar (`~/.config/waybar/config.jsonc`)
Add `"group/niritabs"` to your `modules-left` and include the definitions from `config.jsonc.example`.

### 4. Add Waybar CSS (`~/.config/waybar/style.css`)
Incorporate the CSS from `style.css.example`.

### 5. Reload Waybar
```bash
pkill waybar && sleep 0.5 && niri msg action spawn -- waybar
```

---

## License

MIT © [yesvus](https://github.com/yesvus)
