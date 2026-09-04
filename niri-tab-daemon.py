#!/usr/bin/env python3
"""
Event-driven Waybar taskbar daemon for Niri.
Maintains individual Firefox-style tab states in /dev/shm/niri-tabs/
with integrated close buttons and Niri-aligned behavior.
"""

import os
import sys
import json
import subprocess
import signal
import html

SHM_DIR = "/dev/shm/niri-tabs"
NUM_SLOTS = 6
MAX_TITLE_LEN = 8

def fade_title(title, max_len=8):
    title = html.escape(title)
    if len(title) <= max_len:
        return title
    # Gradient fade of trailing characters into the tab background (like Firefox)
    lead = title[:max_len - 3]
    c1 = title[max_len - 3] if len(title) > max_len - 3 else ""
    c2 = title[max_len - 2] if len(title) > max_len - 2 else ""
    c3 = title[max_len - 1] if len(title) > max_len - 1 else ""
    return f'{lead}<span alpha="70%">{c1}</span><span alpha="40%">{c2}</span><span alpha="15%">{c3}</span>'

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

    total_workspaces = len(wss)


    state_sig = (
        total_workspaces,
        focused_ws,
        total,
        left_overflow,
        right_overflow,
        [(w.get("id"), w.get("is_focused"), w.get("title")) for w in visible]
    )
    current_hash = hash(str(state_sig))
    if current_hash == last_state_hash:
        return
    last_state_hash = current_hash

    os.makedirs(SHM_DIR, exist_ok=True)

    # 1. Left & right pagination arrows and overflow fades
    page_prev_file = os.path.join(SHM_DIR, "page-prev.json")
    page_next_file = os.path.join(SHM_DIR, "page-next.json")
    fade_left_file = os.path.join(SHM_DIR, "fade-left.json")
    fade_right_file = os.path.join(SHM_DIR, "fade-right.json")

    # Left pagination button & fade: appear ONLY when there is left overflow
    if left_overflow > 0:
        prev_tip = f"Scroll left ({left_overflow} window(s) to the left)"
        write_json(page_prev_file, {
            "text": "‹",
            "tooltip": prev_tip,
            "class": "page-prev"
        })
        write_json(fade_left_file, {
            "text": " ",
            "tooltip": prev_tip,
            "class": "fade-left"
        })
    else:
        write_json(page_prev_file, {"text": "", "tooltip": "", "class": ""})
        write_json(fade_left_file, {"text": "", "tooltip": "", "class": ""})

    # Right pagination button & fade: appear ONLY when there is right overflow
    if right_overflow > 0:
        next_tip = f"Scroll right ({right_overflow} window(s) to the right)"
        write_json(page_next_file, {
            "text": "›",
            "tooltip": next_tip,
            "class": "page-next"
        })
        write_json(fade_right_file, {
            "text": " ",
            "tooltip": next_tip,
            "class": "fade-right"
        })
    else:
        write_json(page_next_file, {"text": "", "tooltip": "", "class": ""})
        write_json(fade_right_file, {"text": "", "tooltip": "", "class": ""})

    # 2. Tab slots (Tab body + Tab close button)
    for slot in range(NUM_SLOTS):
        tab_json_file = os.path.join(SHM_DIR, f"tab-{slot}.json")
        close_json_file = os.path.join(SHM_DIR, f"tab-close-{slot}.json")
        slot_id_file = os.path.join(SHM_DIR, f"slot-{slot}.id")

        if slot < len(visible):
            w = visible[slot]
            win_id = w.get("id", 0)
            app_id = w.get("app_id") or ""
            title = (w.get("title") or app_id or "window").strip()
            if title.startswith("✳ "):
                title = title[2:].strip()

            icon = get_icon(app_id, title)
            short_title = fade_title(title, MAX_TITLE_LEN)

            is_focused = w.get("is_focused", False)
            css_class = "active" if is_focused else "normal"

            # Tab body
            tab_data = {
                "text": f"{icon} {short_title}",
                "tooltip": f"[{win_id}] {title}\nLeft-click: Focus window\nMiddle-click: Close window",
                "class": css_class
            }
            write_json(tab_json_file, tab_data)

            # Close button (minimal ×)
            close_data = {
                "text": "✕",
                "tooltip": f"Close {title}",
                "class": css_class
            }
            write_json(close_json_file, close_data)
            write_text(slot_id_file, str(win_id))
        else:
            write_json(tab_json_file, {"text": "", "tooltip": "", "class": ""})
            write_json(close_json_file, {"text": "", "tooltip": "", "class": ""})
            write_text(slot_id_file, "")

    # Signal Waybar to reload custom modules
    subprocess.run(["pkill", "-RTMIN+1", "waybar"], stderr=subprocess.DEVNULL)

def main():
    def handle_signal(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    update_tabs()

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
