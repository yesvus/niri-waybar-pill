# niri-waybar-pill 💊

A collection of minimal, compact, pill-styled window management solutions for the [Niri](https://github.com/niri-wm/niri) scrollable tiling window manager and [Waybar](https://github.com/Alexays/Waybar).

Designed for users who want borderless, CSD-free terminal windows without sacrificing window titles, quick window controls, or taskbar access.

---

## What's Included

### 1. Workspace-Filtered Compact Taskbar (`niri-taskbar.py`) ⭐ *(New)*
* **Workspace-Aware:** Only renders windows that belong to the **currently active workspace** (doesn't dump all windows from other workspaces onto your bar).
* **Non-Grouped (Windows Style):** Every window is its own separate, distinct pill (not merged into one app bundle like macOS).
* **Compact & Fixed Width:** Each tab is formatted to a fixed width (icon + truncated title), giving your bar an organized, neat aesthetic.
* **Focused Window Glow:** The active window is highlighted with bold text and a brighter pill background.
* **Overflow Protection:** Automatically caps visible tabs to 6 and displays a `+N` indicator if your workspace ribbon has many windows, ensuring Waybar never exceeds screen width.
* **Mouse Interactions:**
  * **Left Click:** Opens Niri overview (`toggle-overview`) to click and jump directly to any window.
  * **Scroll Up / Down:** Cycles focus to the left/right window on the workspace ribbon.
  * **Right Click:** Closes the active window.

### 2. Workspace Window Counter (`niri-wincount.py`)
* Event-driven radar daemon (`󱂬 <count>`) tracking how many windows are currently in your scrollable workspace strip.
* Zero CPU overhead (listens directly to `niri msg -j event-stream`).

---

## Installation

### 1. Copy the Script
```bash
cp niri-taskbar.py ~/.config/waybar/
chmod +x ~/.config/waybar/niri-taskbar.py
```

### 2. Configure Waybar (`~/.config/waybar/config.jsonc`)
Add `"custom/niritaskbar"` to your `modules-left`:

```jsonc
"modules-left": ["custom/archmenu", "custom/launcher", "group/workspacesview", "custom/niritaskbar"],

"custom/niritaskbar": {
    "exec": "~/.config/waybar/niri-taskbar.py",
    "return-type": "json",
    "format": "{}",
    "tooltip": true,
    "on-click": "niri msg action toggle-overview",
    "on-click-right": "niri msg action close-window",
    "on-scroll-up": "niri msg action focus-column-left",
    "on-scroll-down": "niri msg action focus-column-right"
}
```

### 3. Add Waybar CSS (`~/.config/waybar/style.css`)
```css
#custom-niritaskbar {
    background-color: transparent;
    font-size: 8pt;
    font-weight: normal;
    padding: 1px 10px;
}
```

### 4. Reload Waybar
```bash
pkill -USR2 waybar
```

---

## License

MIT © [yesvus](https://github.com/yesvus)
