#!/usr/bin/env python3
"""
Event-driven Waybar taskbar for Niri.
Renders all windows in the CURRENT focused workspace as compact, fixed-width pills.
"""

import subprocess
import json
import sys
import html

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

def format_tab(w, max_len=9):
    app_id = w.get("app_id") or ""
    title = (w.get("title") or app_id or "window").strip()
    if title.startswith("✳ "):
        title = title[2:].strip()

    icon = get_icon(app_id, title)
    is_focused = w.get("is_focused", False)

    if len(title) > max_len:
        short = title[:max_len - 1] + "…"
    else:
        short = title.ljust(max_len)

    label = html.escape(f" {icon} {short} ")

    if is_focused:
        return (
            f'<span background="rgba(255,255,255,0.22)" '
            f'foreground="#ffffff" '
            f'font_weight="bold">{label}</span>'
        )
    else:
        return (
            f'<span background="rgba(255,255,255,0.06)" '
            f'foreground="rgba(222,222,222,0.60)">{label}</span>'
        )

last_output = None

def render_taskbar():
    global last_output
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

    if not focused_ws:
        _emit({"text": "", "tooltip": "No active workspace"})
        return

    # Filter to current workspace ONLY
    active_wins = [w for w in wins if w.get("workspace_id") == focused_ws]

    def sort_key(w):
        layout = w.get("layout", {})
        pos = layout.get("pos_in_scrolling_layout")
        if pos and isinstance(pos, (list, tuple)) and len(pos) >= 1:
            return pos[0]
        return w.get("id", 0)

    active_wins.sort(key=sort_key)

    if not active_wins:
        _emit({"text": "", "tooltip": "Workspace empty"})
        return

    MAX_TABS = 6
    total = len(active_wins)

    focused_idx = 0
    for i, w in enumerate(active_wins):
        if w.get("is_focused"):
            focused_idx = i
            break

    if total <= MAX_TABS:
        visible = active_wins
        overflow = 0
    else:
        start = max(0, min(focused_idx - (MAX_TABS // 2), total - MAX_TABS))
        visible = active_wins[start:start + MAX_TABS]
        overflow = total - len(visible)

    tabs = [format_tab(w) for w in visible]
    rendered = " ".join(tabs)

    if overflow > 0:
        rendered += f' <span foreground="rgba(222,222,222,0.40)">+{overflow}</span>'

    tooltip_lines = [
        f"{'●' if w.get('is_focused') else '○'} [{w.get('id')}] {w.get('title') or w.get('app_id')}"
        for w in active_wins
    ]

    payload = {
        "text": rendered,
        "tooltip": "\n".join(tooltip_lines)
    }
    _emit(payload)

def _emit(payload):
    global last_output
    dump = json.dumps(payload)
    if dump != last_output:
        last_output = dump
        sys.stdout.write(dump + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    render_taskbar()
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
                if any(k in ev for k in ("WindowsChanged", "WindowFocusChanged", "WorkspacesChanged", "WorkspaceActivated")):
                    render_taskbar()
            except Exception:
                pass
    except Exception:
        pass
