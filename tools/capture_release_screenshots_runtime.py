from __future__ import absolute_import, division, print_function

import json
import os

try:
    from PySide6 import QtCore, QtTest
except Exception:
    from PySide2 import QtCore, QtTest

import aminate_mobu
import aminate_mobu_history


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOT_ROOT = os.path.join(REPO_ROOT, "docs", "screenshots")
TAB_SCREENSHOTS = [
    (0, "aminate-scene-cleanup.png"),
    (1, "aminate-hik-mapping.png"),
    (2, "aminate-setup-warnings.png"),
    (3, "aminate-constraints-manager.png"),
    (4, "aminate-history-tab.png"),
]
HISTORY_SCREENSHOT = "aminate-history-timeline.png"


def _process_events(app, count=4):
    for _index in range(count):
        app.processEvents()


def run():
    os.makedirs(SCREENSHOT_ROOT, exist_ok=True)
    app = aminate_mobu._qt_application()
    main = aminate_mobu._qt_host_main_window()
    dock = aminate_mobu.launch_aminate_mobu()
    panel = aminate_mobu._QT_TOOL
    if app is None or main is None or dock is None or panel is None:
        raise RuntimeError("MotionBuilder and Aminate must be open before screenshot capture.")

    history_window = aminate_mobu_history.GLOBAL_WINDOW
    if aminate_mobu_history._qt_object_is_valid(history_window):
        history_window.close()
        _process_events(app)

    panel._apply_theme(aminate_mobu.THEME_MODERN)
    aminate_mobu.set_prop_marker_base_name(aminate_mobu.DEFAULT_PROP_MARKER_BASE_NAME)
    panel.prop_marker_base_field.setText(aminate_mobu.DEFAULT_PROP_MARKER_BASE_NAME)
    panel._refresh_definition_manager()
    if str(panel.definition_combo.currentText()).startswith("CodexTabAudit_"):
        panel.definition_combo.clear()
    if str(panel.definition_name_field.text()).startswith("CodexTabAudit_"):
        panel.definition_name_field.clear()
    aminate_mobu._set_status_lines(aminate_mobu._tool_intro_lines())
    try:
        main.resizeDocks([dock], [520], QtCore.Qt.Horizontal)
    except Exception:
        pass
    _process_events(app)

    tabs = panel.workflow_tabs
    bar = tabs.tabBar()
    captured = []
    for index, file_name in TAB_SCREENSHOTS:
        rect = bar.tabRect(index)
        QtTest.QTest.mouseClick(
            bar,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
            rect.center(),
        )
        _process_events(app)
        page = tabs.currentWidget()
        scroll_bar = getattr(page, "verticalScrollBar", lambda: None)()
        if scroll_bar is not None:
            scroll_bar.setValue(0)
            _process_events(app, 1)
        path = os.path.join(SCREENSHOT_ROOT, file_name)
        image = main.grab()
        if not image.save(path):
            raise RuntimeError("Could not save screenshot: {0}".format(path))
        captured.append(
            {
                "tab": str(tabs.tabText(index)),
                "path": path,
                "size": [image.width(), image.height()],
            }
        )

    history_window = aminate_mobu_history.launch_motionbuilder_history_timeline()
    history_window.resize(1200, 720)
    history_window.move(main.x() + 160, main.y() + 80)
    history_window.show()
    history_window.raise_()
    _process_events(app)
    history_path = os.path.join(SCREENSHOT_ROOT, HISTORY_SCREENSHOT)
    history_image = history_window.grab()
    if not history_image.save(history_path):
        raise RuntimeError("Could not save History screenshot: {0}".format(history_path))
    captured.append(
        {
            "tab": "History Timeline",
            "path": history_path,
            "size": [history_image.width(), history_image.height()],
        }
    )
    history_window.close()
    _process_events(app)

    tabs.setCurrentIndex(0)
    _process_events(app)
    payload = {
        "ok": True,
        "source": aminate_mobu.__file__,
        "build": aminate_mobu.QT_PANEL_BUILD_VERSION,
        "theme": aminate_mobu.get_active_theme(),
        "window_geometry": [
            main.x(),
            main.y(),
            main.width(),
            main.height(),
        ],
        "captured": captured,
    }
    print("AMINATE_RELEASE_SCREENSHOTS " + json.dumps(payload, sort_keys=True))
    return payload


run()
