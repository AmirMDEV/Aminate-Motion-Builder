import importlib
import json
import os
import sys


REPO = r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder"
REPORT = os.path.join(REPO, "scratch_easy_tooltip_verify.json")

if REPO not in sys.path:
    sys.path.insert(0, REPO)

import aminate_mobu


def clean(text):
    return aminate_mobu._clean_tooltip_key(text)


def find_action(main, label):
    if main is None or aminate_mobu.QtGui is None:
        return None
    for action in main.findChildren(aminate_mobu.QtGui.QAction):
        try:
            if clean(action.text()) == label:
                return action
        except Exception:
            continue
    return None


def find_widget_by_text(main, label):
    app = aminate_mobu._qt_application()
    if app is None or aminate_mobu.QtWidgets is None:
        return None
    for widget in app.allWidgets():
        try:
            text_fn = getattr(widget, "text", None)
            if callable(text_fn) and clean(text_fn()) == label:
                return widget
        except Exception:
            continue
    return None


def find_tab_tooltip(main, label):
    app = aminate_mobu._qt_application()
    if app is None or aminate_mobu.QtWidgets is None:
        return None
    for bar in app.allWidgets():
        if not isinstance(bar, aminate_mobu.QtWidgets.QTabBar):
            continue
        for index in range(bar.count()):
            try:
                if clean(bar.tabText(index)) == label:
                    return bar.tabToolTip(index)
            except Exception:
                continue
    return None


aminate_mobu = importlib.reload(aminate_mobu)
toolbar = aminate_mobu.ensure_motionbuilder_ui_entry()
dock = aminate_mobu.launch_aminate_mobu()
touched = aminate_mobu.install_easy_motionbuilder_tooltips()
main = aminate_mobu._qt_host_main_window()
launcher_widget = None
launcher_toolbar = getattr(aminate_mobu, "_QT_LAUNCHER_TOOLBAR", None)
launcher_action = None
if launcher_toolbar is not None:
    try:
        actions = list(launcher_toolbar.actions())
        launcher_action = actions[0] if actions else None
    except Exception:
        launcher_action = None
if launcher_toolbar is not None and launcher_action is not None:
    try:
        launcher_widget = launcher_toolbar.widgetForAction(launcher_action)
    except Exception:
        launcher_widget = None

payload = {
    "toolbar": bool(toolbar),
    "dock": bool(dock),
    "touched": touched,
    "launcher_widget_tooltip": (
        launcher_widget.toolTip() if launcher_widget is not None else None
    ),
    "launcher_action_tooltip": (
        launcher_action.toolTip() if launcher_action is not None else None
    ),
    "file_menu_tooltip": (
        find_action(main, "File").toolTip() if find_action(main, "File") else None
    ),
    "viewer_tooltip": (
        find_widget_by_text(main, "Viewer").toolTip()
        if find_widget_by_text(main, "Viewer")
        else None
    ),
    "scene_cleaner_tooltip": (
        find_widget_by_text(main, "Scene Cleaner").toolTip()
        if find_widget_by_text(main, "Scene Cleaner")
        else None
    ),
    "navigator_tab_tooltip": find_tab_tooltip(main, "Navigator"),
    "fcurves_tab_tooltip": find_tab_tooltip(main, "FCurves"),
}

with open(REPORT, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)

print(REPORT)
