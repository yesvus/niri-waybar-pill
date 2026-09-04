# niri-waybar-pill 💊

A collection of minimal, compact, pill-styled window management solutions for the [Niri](https://github.com/niri-wm/niri) scrollable tiling window manager and [Waybar](https://github.com/Alexays/Waybar).

Designed for users who want borderless, CSD-free terminal windows without sacrificing window titles, quick window controls, or taskbar access.

---

## What's Included

### 1. Interactive Firefox-Style Tabs (`niri-tab-daemon.py` & `niri-tab-action.sh`) 🚀 *(Recommended)*
* **Seamless Firefox Pills:** Each window tab is rendered as a clean, unified pill with an integrated minimal close button (`󰅖`) at the right end.
* **Direct Window Jumping:** Left-clicking the tab body focuses that specific window immediately (`niri msg action focus-window --id <ID>`).
* **Integrated Close Action:** Left-clicking the integrated close button (or right/middle-clicking the tab body) immediately closes that window (`niri msg action close-window --id <ID>`).
* **No Font-Weight Jitter:** Both active and inactive tabs maintain identical font weight and size (`font-weight: normal; font-size: 8pt;`), eliminating horizontal layout shifts during window focus changes.
* **Minimal `‹` and `›` Pagination:** Icon-only navigation arrows with transparent backgrounds and hover highlighting.
* **Niri Ribbon-Aligned Overflow Scroll Fade:** Subtle horizontal gradient fades on `+N` overflow badges mirroring Niri's infinite horizontal ribbon.
* **Smooth Easing Transitions:** Calibrated with `transition: all 150ms cubic-bezier(0.215, 0.61, 0.355, 1);` matching Niri's default `ease-out-cubic` curve.

### 2. Single-Module Workspace Taskbar (`niri-taskbar.py`)
* Lightweight single-span taskbar for minimal setups.
* Left-click toggles overview, scroll cycles windows.

### 3. Workspace Window Counter (`niri-wincount.py`)
* Event-driven radar daemon (`󱂬 <count>`) tracking how many windows are currently in your scrollable workspace strip.

---

## Quick Setup (Firefox-Style Tabs)

### 1. Copy Daemon & Action Handler
```bash
cp niri-tab-daemon.py niri-tab-action.sh ~/.config/waybar/
chmod +x ~/.config/waybar/niri-tab-daemon.py ~/.config/waybar/niri-tab-action.sh
```

### 2. Configure Waybar (`~/.config/waybar/config.jsonc`)
Add `"group/niritabs"` to your `modules-left` and include the definitions from `config.jsonc.example`.

### 3. Add Waybar CSS (`~/.config/waybar/style.css`)
Incorporate the CSS from `style.css.example`.

### 4. Reload Waybar
```bash
pkill waybar && sleep 0.5 && niri msg action spawn -- waybar
```

---

## License

MIT © [yesvus](https://github.com/yesvus)
