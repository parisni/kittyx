"""Companion shell paired with the active window in its tab: with the stack
layout it stays a hidden layer behind its parent (e.g. helix). See README."""

import os
import subprocess

from kitty.boss import Boss
from kittens.tui.handler import result_handler

# User var linking a companion to its parent; tools listing windows (e.g.
# dfzf) match on it, so keep the name stable.
COMPANION_VAR = "kittyx_companion"


def main(args: list[str]) -> None:
    pass


def find_companion(tab, parent):
    for window in tab:
        if window.user_vars.get(COMPANION_VAR) == str(parent.id):
            return window
    return None


def wm_focus(direction: str) -> None:
    # The kitty mapping replaces the window manager's focus binding, so past the
    # pair's edge the move is handed back to it; no-op elsewhere (e.g. macOS).
    if os.environ.get("SWAYSOCK"):
        cmd = "swaymsg"
    elif os.environ.get("I3SOCK"):
        cmd = "i3-msg"
    else:
        return
    try:
        subprocess.run([cmd, "-q", "focus", direction], timeout=2,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


@result_handler(no_ui=True)
def handle_result(args: list[str], answer: str, target_window_id: int, boss: Boss) -> None:
    window = boss.window_id_map.get(target_window_id)
    tab = window.tabref() if window is not None else None
    if tab is None:
        return
    action = args[1] if len(args) > 1 else "toggle"

    parent_id = window.user_vars.get(COMPANION_VAR)
    if parent_id:
        # Pressed from the companion itself, which sits below its parent.
        if action == "close":
            boss.mark_window_for_close(window)
            return
        if action == "down":
            wm_focus("down")
            return
        parent = boss.window_id_map.get(int(parent_id))
        if parent is not None:
            boss.set_active_window(parent)
        elif action == "up":
            wm_focus("up")
        return

    companion = find_companion(tab, window)
    if action == "close":
        if companion is not None:
            boss.mark_window_for_close(companion)
    elif action == "up" or (action == "down" and companion is None):
        wm_focus(action)
    elif companion is not None:
        boss.set_active_window(companion)
    else:
        # --cwd=current: the parent's foreground process cwd (e.g. helix's project).
        boss.call_remote_control(window, (
            "launch", "--self", "--type=window", "--cwd=current",
            f"--var={COMPANION_VAR}={window.id}",
        ))
