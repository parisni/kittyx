"""Companion shell paired with the active window in its tab: with the stack
layout it stays a hidden layer behind its parent (e.g. helix). See README."""

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


@result_handler(no_ui=True)
def handle_result(args: list[str], answer: str, target_window_id: int, boss: Boss) -> None:
    window = boss.window_id_map.get(target_window_id)
    tab = window.tabref() if window is not None else None
    if tab is None:
        return
    closing = args[1:2] == ["close"]

    parent_id = window.user_vars.get(COMPANION_VAR)
    if parent_id:
        # Pressed from the companion itself: close it or go back to its parent.
        if closing:
            boss.mark_window_for_close(window)
            return
        parent = boss.window_id_map.get(int(parent_id))
        if parent is not None:
            boss.set_active_window(parent)
        return

    companion = find_companion(tab, window)
    if closing:
        if companion is not None:
            boss.mark_window_for_close(companion)
    elif companion is not None:
        boss.set_active_window(companion)
    else:
        # --cwd=current: the parent's foreground process cwd (e.g. helix's project).
        boss.call_remote_control(window, (
            "launch", "--self", "--type=window", "--cwd=current",
            f"--var={COMPANION_VAR}={window.id}",
        ))
