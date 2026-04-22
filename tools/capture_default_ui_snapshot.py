from __future__ import annotations

import importlib
import os
import sys


REPO_ROOT = r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder"


def main():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    import aminate_mobu  # pylint: disable=import-error

    aminate_mobu = importlib.reload(aminate_mobu)
    panel = aminate_mobu.launch_aminate_mobu()
    if hasattr(panel, "panel"):
        panel = panel.panel
    snapshot_path = aminate_mobu.capture_current_ui_snapshot()
    main_window = aminate_mobu._qt_host_main_window()
    screenshot_path = os.path.join(REPO_ROOT, "motionbuilder_default_ui_snapshot.png")
    if main_window is not None:
        try:
            main_window.grab().save(screenshot_path)
        except Exception:
            screenshot_path = ""
    print(snapshot_path or "")
    print(screenshot_path)
    print(panel.theme_badge.text() if hasattr(panel, "theme_badge") else "")


if __name__ == "__main__":
    main()
