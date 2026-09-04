#!/usr/bin/env python3
"""
Event-driven Waybar taskbar daemon for Niri.
Maintains individual tab states in /dev/shm/niri-tabs/ for interactive,
clickable pills that jump directly to windows on click.
"""

import os
import sys
import json
import subprocess
import html
import signal

SHM_DIR = "/dev/shm/niri-tabs"
NUM_SLOTS = 7
MAX_TITLE_LEN = 10

APP_ICONS = {
    "firefox": "󰈹",
    "chromium": "󰊯",
    "google-chrome": "󰊯",
    "ghostty": "",
    "foot": "",
    "alacritty": "",
    "kitty": "",
    "dev.zed.zed": "󰨞",
    "code": "󰨞",
    "vscodium": "󰨞",
    "discord": "󰙯",
    "vesktop": "󰙯",
    "telegram": "󰈰",
    "spotify": "󰓇",
    "slack": "󰒱",
    "obsidian": "󰠮",
    "nemo": "󰉋",
    "thunar": "󰉋",
    "nautilus": "󰉋",
    "btop": "󰌓",
    "default": ""
}

def get_icon(app_id, title):
    app = (app_id or "").lower()
    t = (title or "").lower()
    for key, icon in APP_ICONS.items():
        if key in app or key in t:
            return icon
    return APP_ICONS["default"]

def write_json(path, data):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp_path, path)

def write_text(path, text):
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp_path, path)

last_state_hash = None

def update_tabs():
    global last_state_hash
    try:
        wins_raw = subprocess.check_output(["niri", "msg", "-j", "windows"], stderr=subprocess.DEVNULL)
        wss_raw = subprocess.check_output(["niri", "msg", "-j", "workspaces"], stderr=subprocess.DEVNULL)
        wins = json.loads(wins_raw)
        wss = json.loads(wss_raw)
    except Exception:
        return

    focused_ws = next((ws["id"] for ws in wss if ws.get("is_focused")), None)
    if not focused_ws:
        focused_ws = next((w.get("workspace_id") for w in wins if w.get("is_focused")), None)

    active_wins = [w for w in wins if w.get("workspace_id") == focused_ws] if focused_ws else []

    def sort_key(w):
        layout = w.get("layout", {})
        pos = layout.get("pos_in_scrolling_layout")
        if pos and isinstance(pos, (list, tuple)) and len(pos) >= 1:
            return pos[0]
        return w.get("id", 0)

    active_wins.sort(key=sort_key)
    total = len(active_wins)

    focused_idx = 0
    for i, w in enumerate(active_wins):
        if w.get("is_focused"):
            focused_idx = i
            break

    if total <= NUM_SLOTS:
        start = 0
        visible = active_wins
        left_overflow = 0
        right_overflow = 0
    else:
        start = max(0, min(focused_idx - (NUM_SLOTS // 2), total - NUM_SLOTS))
        visible = active_wins[start:start + NUM_SLOTS]
        left_overflow = start
        right_overflow = total - (start + len(visible))

    # Fast hash check to avoid redundant disk writes and signals
    state_sig = (
        focused_ws,
        left_overflow,
        right_overflow,
        [(w.get("id"), w.get("is_focused"), w.get("title")) for w in visible]
    )
    current_hash = hash(str(state_sig))
    if current_hash == last_state_hash:
        return
    last_state_hash = current_hash

    os.makedirs(SHM_DIR, exist_ok=True)

    # 1. Left overflow indicator
    left_file = os.path.join(SHM_DIR, "tab-left.json")
    if left_overflow > 0:
        write_json(left_file, {
            "text": f"+{left_overflow}",
            "tooltip": f"{left_overflow} window(s) to the left\nClick to scroll left",
            "class": "overflow"
        })
    else:
        write_json(left_file, {"text": "", "tooltip": "", "class": ""})

    # 2. Tab slots
    for slot in range(NUM_SLOTS):
        tab_json_file = os.path.join(SHM_DIR, f"tab-{slot}.json")
        slot_id_file = os.path.join(SHM_DIR, f"slot-{slot}.id")

        if slot < len(visible):
            w = visible[slot]
            win_id = w.get("id", 0)
            app_id = w.get("app_id") or ""
            title = (w.get("title") or app_id or "window").strip()
            if title.startswith("✳ "):
                title = title[2:].strip()

            icon = get_icon(app_id, title)
            if len(title) > MAX_TITLE_LEN:
                short_title = title[:MAX_TITLE_LEN - 1] + "…"
            else:
                short_title = title.ljust(MAX_TITLE_LEN)

            is_focused = w.get("is_focused", False)
            css_class = "active" if is_focused else "normal"

            tab_data = {
                "text": f"{icon} {short_title}",
                "tooltip": f"[{win_id}] {title}\nLeft-click: Jump to window\nRight-click: Close window",
                "class": css_class
            }
            write_json(tab_json_file, tab_data)
            write_text(slot_id_file, str(win_id))
        else:
            write_json(tab_json_file, {"text": "", "tooltip": "", "class": ""})
            write_text(slot_id_file, "")

    # 3. Right overflow indicator
    right_file = os.path.join(SHM_DIR, "tab-right.json")
    if right_overflow > 0:
        write_json(right_file, {
            "text": f"+{right_overflow}",
            "tooltip": f"{right_overflow} window(s) to the right\nClick to scroll right",
            "class": "overflow"
        })
    else:
        write_json(right_file, {"text": "", "tooltip": "", "class": ""})

    # Signal Waybar to reload custom modules on RTMIN+1
    subprocess.run(["pkill", "-RTMIN+1", "waybar"], stderr=subprocess.DEVNULL)

def main():
    def handle_signal(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Initial render
    update_tabs()

    # Event stream
    try:
        proc = subprocess.Popen(
            ["niri", "msg", "-j", "event-stream"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
            stderr=subprocess.DEVNULL
        )
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if any(k in ev for k in (
                    "WindowsChanged",
                    "WindowFocusChanged",
                    "WindowOpenedOrChanged",
                    "WindowClosed",
                    "WorkspacesChanged",
                    "WorkspaceActivated",
                    "WorkspaceActiveWindowChanged"
                )):
                    update_tabs()
            except Exception:
                pass
    except Exception:
        pass

if __name__ == "__main__":
    main()
