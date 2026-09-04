# niri-waybar-pill 💊

A collection of minimal, compact, pill-styled window management solutions for the [Niri](https://github.com/niri-wm/niri) scrollable tiling window manager and [Waybar](https://github.com/Alexays/Waybar).

Designed for users who want borderless, CSD-free terminal windows without sacrificing window titles, quick window controls, or taskbar access.

---

## Features

### 1. Compact Windows-style Taskbar (`wlr/taskbar`)
* **Individual Window Instances:** Every window appears as its own compact pill button (not grouped into a single app bundle like macOS).
* **Reduced Border Radius:** Sleek, subtle 5px radius instead of oversized round bubbles.
* **Overflow Handling:** Compact truncation (`max-length: 18`) with tooltips showing full titles.
* **Direct Actions:**
  * **Left Click:** Activate / focus that window (`niri msg action focus-window`).
  * **Middle Click:** Close that window (`niri msg action close-window`).

### 2. Floating Window Pill (`niri-wincount.py` + controls)
* **Active Window Title:** Displays the focused window name cleanly.
* **Workspace Window Radar:** Event-driven counter (`󱂬 <count>`) tracking how many windows are currently on your scrollable workspace strip.
* **Instant Window Controls:** Integrated Maximize (`󰘖`) and Close (``) buttons directly in Waybar.
* **Zero CPU Overhead:** The Python daemon listens directly to `niri msg -j event-stream` and only computes when window/workspace events occur.

---

## Installation

### 1. Setup the Script
Copy the event stream counter script to your Waybar config directory:
```bash
cp niri-wincount.py ~/.config/waybar/
chmod +x ~/.config/waybar/niri-wincount.py
```

### 2. Configure Waybar
Add the desired module (or both!) into your `~/.config/waybar/config.jsonc`:
See [config.jsonc.example](config.jsonc.example).

### 3. Add Styling
Append the CSS rules from [style.css.example](style.css.example) into your `~/.config/waybar/style.css`.

### 4. Reload Waybar
```bash
pkill -USR2 waybar
```

---

## License

MIT © [yesvus](https://github.com/yesvus)
