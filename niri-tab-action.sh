#!/usr/bin/env bash
# Action handler for Waybar Niri tabs
set -euo pipefail

action="${1:?usage: niri-tab-action.sh focus|close|maximize <slot> OR scroll-left|scroll-right}"

case "$action" in
    scroll-left)
        if [[ -f /dev/shm/niri-tabs/has-left-overflow ]]; then
            niri msg action focus-column-left
        fi
        exit 0
        ;;
    scroll-right)
        if [[ -f /dev/shm/niri-tabs/has-right-overflow ]]; then
            niri msg action focus-column-right
        fi
        exit 0
        ;;
esac

slot="${2:?usage: niri-tab-action.sh focus|close|maximize <slot>}"
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
    maximize)
        niri msg action focus-window --id "$win_id"
        niri msg action maximize-window-to-edges
        ;;
esac
