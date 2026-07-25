from __future__ import annotations

import json
import os

try:
    from PySide6 import QtCore, QtTest
except Exception:
    from PySide2 import QtCore, QtTest

import aminate_mobu


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROOF_DIR = os.path.join(REPO_ROOT, ".codex-proof")
REPORT = os.path.join(PROOF_DIR, "motionbuilder_ui_restore_report.json")
MODERN_SCREENSHOT = os.path.join(PROOF_DIR, "motionbuilder_modern.png")
RESTORED_SCREENSHOT = os.path.join(PROOF_DIR, "motionbuilder_restored_native.png")


def _process_events(app, count=4):
    for _index in range(count):
        app.processEvents()


def run():
    os.makedirs(PROOF_DIR, exist_ok=True)

    app = aminate_mobu._qt_application()
    main = aminate_mobu._qt_host_main_window()
    dock = aminate_mobu.launch_aminate_mobu()
    panel = aminate_mobu._QT_TOOL
    if app is None or main is None or panel is None or dock is None:
        raise RuntimeError("Aminate and the MotionBuilder Qt host must be open before verification.")

    panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
    _process_events(app)
    aminate_mobu._sync_baseline_from_app_cache(app)
    baseline_stylesheet = aminate_mobu._APP_THEME_BASELINE
    baseline_palette = aminate_mobu._copy_palette(aminate_mobu._APP_THEME_BASELINE_PALETTE)
    if baseline_stylesheet is None or baseline_palette is None:
        raise RuntimeError("MotionBuilder native theme baseline is unavailable.")

    geometry_before = bytes(main.saveGeometry().toBase64()).decode("ascii")
    layout_before = bytes(main.saveState().toBase64()).decode("ascii")
    dock_before = [dock.x(), dock.y(), dock.width(), dock.height(), bool(dock.isFloating())]

    panel._apply_theme(aminate_mobu.THEME_MODERN)
    _process_events(app)
    main.grab().save(MODERN_SCREENSHOT)
    modern_state = {
        "theme": aminate_mobu.get_active_theme(),
        "button_text": panel.theme_button.text(),
        "app_stylesheet_len": len(app.styleSheet() or ""),
        "app_differs_from_baseline": (app.styleSheet() or "") != (baseline_stylesheet or "")
        and not aminate_mobu._palettes_match(app.palette(), baseline_palette),
    }

    QtTest.QTest.mouseClick(panel.theme_button, QtCore.Qt.LeftButton)
    _process_events(app)
    main.grab().save(RESTORED_SCREENSHOT)
    dock_after = [dock.x(), dock.y(), dock.width(), dock.height(), bool(dock.isFloating())]
    restored_state = {
        "theme": aminate_mobu.get_active_theme(),
        "button_text": panel.theme_button.text(),
        "app_stylesheet_len": len(app.styleSheet() or ""),
        "stylesheet_equals_baseline": (app.styleSheet() or "") == (baseline_stylesheet or ""),
        "palette_equals_baseline": aminate_mobu._palettes_match(app.palette(), baseline_palette),
        "theme_owned": aminate_mobu._APP_THEME_OWNED,
        "geometry_unchanged": bytes(main.saveGeometry().toBase64()).decode("ascii") == geometry_before,
        "layout_state_unchanged": bytes(main.saveState().toBase64()).decode("ascii") == layout_before,
        "dock_geometry_unchanged": dock_after == dock_before,
    }

    payload = {
        "source": os.path.abspath(aminate_mobu.__file__),
        "window_title": main.windowTitle(),
        "window_geometry": [
            main.geometry().x(),
            main.geometry().y(),
            main.geometry().width(),
            main.geometry().height(),
        ],
        "baseline_stylesheet_len": len(baseline_stylesheet or ""),
        "modern": modern_state,
        "restored": restored_state,
        "modern_screenshot": MODERN_SCREENSHOT,
        "restored_screenshot": RESTORED_SCREENSHOT,
    }
    payload["ok"] = bool(
        modern_state["theme"] == aminate_mobu.THEME_MODERN
        and modern_state["app_differs_from_baseline"]
        and restored_state["theme"] == aminate_mobu.THEME_MOTIONBUILDER
        and restored_state["stylesheet_equals_baseline"]
        and restored_state["palette_equals_baseline"]
        and restored_state["theme_owned"] is False
        and restored_state["geometry_unchanged"]
        and restored_state["dock_geometry_unchanged"]
    )

    with open(REPORT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print("AMINATE_DEFAULT_UI_RESTORE " + json.dumps(payload, sort_keys=True))
    if not payload["ok"]:
        raise RuntimeError("Modern-to-MotionBuilder UI restoration failed.")
    return payload


run()
