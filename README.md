# niri-waybar-pill 💊

A collection of minimal, compact, pill-styled window management solutions for the [Niri](https://github.com/niri-wm/niri) scrollable tiling window manager and [Waybar](https://github.com/Alexays/Waybar).

Designed for users who want borderless, CSD-free terminal windows without sacrificing window titles, quick window controls, or taskbar access.

---

## What's Included

### 1. Interactive Workspace Tabs (`niri-tab-daemon.py` & `niri-tab-action.sh`) 🚀 *(Recommended)*
* **Direct Window Jumping:** Clicking any tab immediately focuses that specific window without having to open the workspace overview.
* **Independent Close on Right Click:** Right-clicking any tab immediately closes that window (`niri msg action close-window --id <ID>`).
* **Real GTK Pill Buttons:** Each tab is an individual GTK widget with rounded corners (`border-radius: 5px`), hover lighting, and focused active glow.
* **Bidirectional Dynamic Overflow:** Displays `‹N` on the left when off-screen windows exist to the left, and `+N` on the right when off-screen windows exist to the right. Both update continuously as you navigate through windows.
* **Integrated Window Controls (`group/wincontrols`):** Dedicated pill buttons for **Maximize / Restore** (`󰘖`) and **Close** (``) with custom hover accent colors.

### 2. Single-Module Workspace Taskbar (`niri-taskbar.py`)
* Lightweight single-span taskbar for minimal setups.
* Left-click toggles overview, scroll cycles windows.

### 3. Workspace Window Counter (`niri-wincount.py`)
* Event-driven radar daemon (`󱂬 <count>`) tracking how many windows are currently in your scrollable workspace strip.

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
