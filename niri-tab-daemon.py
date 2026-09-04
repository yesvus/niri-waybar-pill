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
CONFIG_PATH = os.path.expanduser("~/.config/niri-tabs/config.json")

DEFAULT_CONFIG = {
    "max_slots": 6,
    "max_title_len": 8,
    "reserve_navigation": True,
    "show_close_button": True,
    "show_maximize_button": False,
    "close_icon": "✕",
    "maximize_icon": "□"
}

_config_mtime = 0
_cached_config = dict(DEFAULT_CONFIG)

def get_config():
    global _config_mtime, _cached_config
    if os.path.isfile(CONFIG_PATH):
        try:
            mtime = os.path.getmtime(CONFIG_PATH)
            if mtime != _config_mtime:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    content = f.read()
                lines = []
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("//") or stripped.startswith("#"):
                        continue
                    lines.append(line)
                cfg = json.loads("\n".join(lines))
                _cached_config = {**DEFAULT_CONFIG, **cfg}
                _config_mtime = mtime
        except Exception:
            pass
    return _cached_config

def fade_title(title, max_len=8):
    title = html.escape(title)
    if len(title) <= max_len:
        return title
    if max_len <= 3:
        return title[:max_len]
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
    cfg = get_config()
    num_slots = min(int(cfg.get("max_slots", 6)), 6)
    max_title_len = int(cfg.get("max_title_len", 8))
    reserve_nav = bool(cfg.get("reserve_navigation", True))
    show_close = bool(cfg.get("show_close_button", True))
    show_maximize = bool(cfg.get("show_maximize_button", False))
    close_icon = str(cfg.get("close_icon", "✕"))
    maximize_icon = str(cfg.get("maximize_icon", "□"))

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

    if total <= num_slots:
        start = 0
        visible = active_wins
        left_overflow = 0
        right_overflow = 0
    else:
        start = max(0, min(focused_idx - (num_slots // 2), total - num_slots))
        visible = active_wins[start:start + num_slots]
        left_overflow = start
        right_overflow = total - (start + len(visible))

    total_workspaces = len(wss)

    state_sig = (
        num_slots,
        max_title_len,
        reserve_nav,
        show_close,
        show_maximize,
        close_icon,
        maximize_icon,
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
    left_flag_file = os.path.join(SHM_DIR, "has-left-overflow")
    right_flag_file = os.path.join(SHM_DIR, "has-right-overflow")

    # Left pagination button & fade: appear when there is left overflow; reserve space when enabled
    if left_overflow > 0:
        try:
            open(left_flag_file, "a").close()
        except Exception:
            pass
        prev_tip = f"Scroll left ({left_overflow} window(s) to the left)"
        write_json(page_prev_file, {
            "text": "‹",
            "tooltip": prev_tip,
            "class": ["page-prev", "active"]
        })
        write_json(fade_left_file, {
            "text": " ",
            "tooltip": prev_tip,
            "class": ["fade-left", "active"]
        })
    else:
        if os.path.exists(left_flag_file):
            try:
                os.remove(left_flag_file)
            except Exception:
                pass
        if reserve_nav:
            write_json(page_prev_file, {
                "text": "‹",
                "tooltip": "",
                "class": ["page-prev", "disabled"]
            })
            write_json(fade_left_file, {
                "text": " ",
                "tooltip": "",
                "class": ["fade-left", "disabled"]
            })
        else:
            write_json(page_prev_file, {"text": "", "tooltip": "", "class": ""})
            write_json(fade_left_file, {"text": "", "tooltip": "", "class": ""})

    # Right pagination button & fade: appear when there is right overflow; reserve space when enabled
    if right_overflow > 0:
        try:
            open(right_flag_file, "a").close()
        except Exception:
            pass
        next_tip = f"Scroll right ({right_overflow} window(s) to the right)"
        write_json(page_next_file, {
            "text": "›",
            "tooltip": next_tip,
            "class": ["page-next", "active"]
        })
        write_json(fade_right_file, {
            "text": " ",
            "tooltip": next_tip,
            "class": ["fade-right", "active"]
        })
    else:
        if os.path.exists(right_flag_file):
            try:
                os.remove(right_flag_file)
            except Exception:
                pass
        if reserve_nav:
            write_json(page_next_file, {
                "text": "›",
                "tooltip": "",
                "class": ["page-next", "disabled"]
            })
            write_json(fade_right_file, {
                "text": " ",
                "tooltip": "",
                "class": ["fade-right", "disabled"]
            })
        else:
            write_json(page_next_file, {"text": "", "tooltip": "", "class": ""})
            write_json(fade_right_file, {"text": "", "tooltip": "", "class": ""})

    # Button class for tab body padding
    if show_close and show_maximize:
        btn_class = "has-both-buttons"
    elif show_close:
        btn_class = "has-close-only"
    elif show_maximize:
        btn_class = "has-maximize-only"
    else:
        btn_class = "no-buttons"

    # 2. Tab slots (Tab body + optional Maximize button + optional Close button)
    for slot in range(6):
        tab_json_file = os.path.join(SHM_DIR, f"tab-{slot}.json")
        maximize_json_file = os.path.join(SHM_DIR, f"tab-maximize-{slot}.json")
        close_json_file = os.path.join(SHM_DIR, f"tab-close-{slot}.json")
        slot_id_file = os.path.join(SHM_DIR, f"slot-{slot}.id")

        if slot < len(visible) and slot < num_slots:
            w = visible[slot]
            win_id = w.get("id", 0)
            app_id = w.get("app_id") or ""
            title = (w.get("title") or app_id or "window").strip()
            if title.startswith("✳ "):
                title = title[2:].strip()

            icon = get_icon(app_id, title)
            short_title = fade_title(title, max_title_len)

            is_focused = w.get("is_focused", False)
            css_class = "active" if is_focused else "normal"

            # Tab body: clean hover tooltip showing only window title
            tab_data = {
                "text": f"{icon} {short_title}",
                "tooltip": title,
                "class": [css_class, btn_class]
            }
            write_json(tab_json_file, tab_data)

            # Optional Maximize/Enlarge button
            if show_maximize:
                max_sub = "with-close" if show_close else "without-close"
                write_json(maximize_json_file, {
                    "text": maximize_icon,
                    "tooltip": "Maximize",
                    "class": [css_class, max_sub]
                })
            else:
                write_json(maximize_json_file, {"text": "", "tooltip": "", "class": ""})

            # Optional Close button
            if show_close:
                close_sub = "with-maximize" if show_maximize else "without-maximize"
                write_json(close_json_file, {
                    "text": close_icon,
                    "tooltip": "Close",
                    "class": [css_class, close_sub]
                })
            else:
                write_json(close_json_file, {"text": "", "tooltip": "", "class": ""})

            write_text(slot_id_file, str(win_id))
        else:
            write_json(tab_json_file, {"text": "", "tooltip": "", "class": ""})
            write_json(maximize_json_file, {"text": "", "tooltip": "", "class": ""})
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
