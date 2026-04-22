from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from pywinauto import Desktop


REPO_ROOT = Path(r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder")
SCREENSHOT_PATH = REPO_ROOT / "motionbuilder_default_ui_reference.png"
REFERENCE_PATH = REPO_ROOT / "motionbuilder_default_ui_reference.json"
CAPTURE_SCRIPT = Path(r"C:\Users\Amir Mansaray\Documents\Github\tools\app-control\capture_app_window.ps1")


def _rect_dict(wrapper):
    rect = wrapper.rectangle()
    return {
        "left": rect.left,
        "top": rect.top,
        "right": rect.right,
        "bottom": rect.bottom,
        "width": rect.width(),
        "height": rect.height(),
    }


def _menu_items(root):
    items = []
    for widget in root.descendants():
        if widget.element_info.control_type != "MenuItem":
            continue
        title = widget.window_text().strip()
        if not title or title == "System":
            continue
        if widget.element_info.class_name != "QAction":
            continue
        if title in items:
            continue
        items.append(title)
    return items


def _tool_windows(root):
    windows = []
    for widget in root.children():
        if widget.element_info.control_type != "Window":
            continue
        title = widget.window_text().strip()
        if not title:
            continue
        windows.append(
            {
                "title": title,
                "class_name": widget.element_info.class_name,
                "rect": _rect_dict(widget),
            }
        )
    return windows


def _toolbars(root):
    toolbars = []
    for widget in root.children():
        if widget.element_info.control_type != "ToolBar":
            continue
        buttons = []
        for child in widget.descendants():
            if child.element_info.control_type != "Button":
                continue
            title = child.window_text().strip() or child.element_info.name or ""
            if title:
                buttons.append(title)
        toolbars.append(
            {
                "title": widget.window_text().strip() or widget.element_info.name or "",
                "class_name": widget.element_info.class_name,
                "rect": _rect_dict(widget),
                "buttons": buttons,
            }
        )
    return toolbars


def capture_reference():
    desktop = Desktop(backend="uia")
    root = desktop.window(title="Mainboard")
    window_title = ""
    desktop_win32 = Desktop(backend="win32")
    for widget in desktop_win32.windows(process=root.process_id()):
        name = widget.window_text().strip()
        if name.startswith("Autodesk MotionBuilder"):
            window_title = name
            break
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(CAPTURE_SCRIPT),
            "-TitleRegex",
            "^Autodesk MotionBuilder",
            "-OutputPath",
            str(SCREENSHOT_PATH),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = {
        "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "process_id": root.process_id(),
        "window_title": window_title,
        "root_title": root.window_text(),
        "root_class_name": root.element_info.class_name,
        "root_rect": _rect_dict(root),
        "top_level_menu_items": _menu_items(root),
        "top_level_tool_windows": _tool_windows(root),
        "toolbars": _toolbars(root),
        "screenshot_path": str(SCREENSHOT_PATH),
    }
    REFERENCE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(str(REFERENCE_PATH))
    print(str(SCREENSHOT_PATH))


if __name__ == "__main__":
    capture_reference()
