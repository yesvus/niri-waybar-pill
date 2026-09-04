#!/usr/bin/env bash
# Action handler for Waybar Niri tabs
set -euo pipefail

action="${1:?usage: niri-tab-action.sh focus|close <slot>}"
slot="${2:?usage: niri-tab-action.sh focus|close <slot>}"
id_file="/dev/shm/niri-tabs/slot-${slot}.id"

[[ -r "$id_file" ]] || exit 0
win_id=$(cat "$id_file" 2>/dev/null || true)
[[ -n "$win_id" ]] || exit 0

case "$action" in
    focus)
        niri msg action focus-window --id "$win_id"
        ;;
    close)
        niri msg action close-window --id "$win_id"
        ;;
esac
