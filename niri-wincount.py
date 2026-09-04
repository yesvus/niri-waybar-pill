#!/usr/bin/env python3
import subprocess
import json
import sys

last_count = None

def get_state():
    try:
        out = subprocess.check_output(["niri", "msg", "-j", "windows"], stderr=subprocess.DEVNULL)
        wins = json.loads(out)
        focused_ws = next((w.get("workspace_id") for w in wins if w.get("is_focused")), None)
        if not focused_ws:
            ws_out = subprocess.check_output(["niri", "msg", "-j", "workspaces"], stderr=subprocess.DEVNULL)
            wss = json.loads(ws_out)
            focused_ws = next((w["id"] for w in wss if w.get("is_focused")), None)
        count = sum(1 for w in wins if w.get("workspace_id") == focused_ws) if focused_ws else 0
        return count
    except Exception:
        return 0

def output_count(count):
    global last_count
    if count == last_count:
        return
    last_count = count
    if count > 0:
        res = {
            "text": f"󱂬 {count}",
            "tooltip": f"{count} window{'s' if count > 1 else ''} on this workspace"
        }
    else:
        res = {"text": "", "tooltip": "Workspace empty"}
    sys.stdout.write(json.dumps(res) + "\n")
    sys.stdout.flush()

output_count(get_state())

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
                output_count(get_state())
        except Exception:
            pass
except Exception:
    pass
