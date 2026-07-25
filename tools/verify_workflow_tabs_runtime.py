from __future__ import absolute_import, division, print_function

import json

import aminate_mobu

try:
    from PySide6 import QtTest
except Exception:
    from PySide2 import QtTest


EXPECTED_TABS = [
    "Cln",
    "HIK",
    "Wrn",
    "Con",
    "Hist",
]

EXPECTED_CONTROLS = {
    "Cln": ["Scene Cleaner", "Delete Cameras", "Delete Markers"],
    "HIK": ["Use Selected Skeleton", "Auto Map Skeleton", "Validate Character"],
    "Wrn": ["Check Setup Now", "Body Part Mode", "Full Body Mode"],
    "Con": ["List Constraints", "Rename To Easy Names", "Save To Control Rig"],
    "Hist": ["History Timeline"],
}


def _button_text(button):
    try:
        return str(button.text())
    except Exception:
        return ""


def run():
    dock = aminate_mobu.launch_aminate_mobu()
    panel = aminate_mobu._QT_TOOL
    if panel is None or dock is None:
        raise RuntimeError("Aminate Mobu Qt panel is not open.")
    if getattr(panel, "_build_version", 0) != aminate_mobu.QT_PANEL_BUILD_VERSION:
        raise RuntimeError("Live Aminate panel build is stale.")

    tabs = panel.workflow_tabs
    labels = [str(tabs.tabText(index)) for index in range(tabs.count())]
    if labels != EXPECTED_TABS:
        raise AssertionError("Unexpected workflow tabs: {0}".format(labels))

    app = aminate_mobu.QtWidgets.QApplication.instance()
    original_width = int(dock.width())
    changed = []
    results = []

    def _on_changed(index):
        changed.append(int(index))

    tabs.currentChanged.connect(_on_changed)
    try:
        bar = tabs.tabBar()
        for index, label in enumerate(EXPECTED_TABS):
            tabs.setCurrentIndex(index)
            app.processEvents()
            other_index = index - 1 if index else 1
            tabs.setCurrentIndex(other_index)
            app.processEvents()
            rect = bar.tabRect(index)
            if not rect.intersects(bar.rect()):
                raise AssertionError("Tab is not reachable at narrow dock width: {0}".format(label))
            QtTest.QTest.mouseClick(
                bar,
                aminate_mobu.QtCore.Qt.LeftButton,
                aminate_mobu.QtCore.Qt.NoModifier,
                rect.center(),
            )
            app.processEvents()
            if tabs.currentIndex() != index:
                raise AssertionError("Click did not select tab {0}".format(label))
            page = tabs.currentWidget()
            buttons = {
                _button_text(button): button
                for button in page.findChildren(aminate_mobu.QtWidgets.QPushButton)
            }
            missing = [caption for caption in EXPECTED_CONTROLS[label] if caption not in buttons]
            if missing:
                raise AssertionError("{0} is missing controls: {1}".format(label, missing))
            results.append(
                {
                    "index": index,
                    "label": label,
                    "page_object": str(page.objectName()),
                    "page_visible": bool(page.isVisible()),
                    "controls": EXPECTED_CONTROLS[label],
                    "tab_rect": [rect.x(), rect.y(), rect.width(), rect.height()],
                }
            )
    finally:
        try:
            tabs.currentChanged.disconnect(_on_changed)
        except Exception:
            pass
        tabs.setCurrentIndex(0)
        app.processEvents()

    payload = {
        "ok": True,
        "source": aminate_mobu.__file__,
        "build": panel._build_version,
        "labels": labels,
        "changed_signals": changed,
        "tabs": results,
        "restored_dock_width": int(dock.width()),
        "current_tab": str(tabs.tabText(tabs.currentIndex())),
    }
    if payload["restored_dock_width"] != original_width:
        raise AssertionError(
            "Tab switching resized the dock from {0} to {1}".format(
                original_width,
                payload["restored_dock_width"],
            )
        )
    print("AMINATE_WORKFLOW_TABS " + json.dumps(payload, sort_keys=True))
    return payload


run()
