from __future__ import absolute_import, division, print_function

import json

import aminate_mobu
import aminate_mobu_history


def _style_pointer(app):
    style = app.style()
    if aminate_mobu.getCppPointer is not None:
        try:
            return int(aminate_mobu.getCppPointer(style)[0])
        except Exception:
            pass
    return id(style)


def _process_events(app, count=3):
    for _index in range(count):
        app.processEvents()


def run():
    app = aminate_mobu._qt_application()
    main = aminate_mobu._qt_host_main_window()
    if app is None or main is None:
        raise RuntimeError("MotionBuilder Qt host is unavailable.")
    if not str(aminate_mobu.__file__).lower().endswith("aminate_mobu.py"):
        raise RuntimeError("Unexpected Aminate module path: {0}".format(aminate_mobu.__file__))

    style_pointer = _style_pointer(app)
    dock = aminate_mobu.launch_aminate_mobu()
    _process_events(app)
    if not aminate_mobu._qt_object_is_valid(dock):
        raise RuntimeError("Aminate dock did not open.")

    launch_ids = []
    for _index in range(5):
        launched = aminate_mobu.launch_aminate_mobu()
        _process_events(app, 1)
        launch_ids.append(id(launched))
        if launched is not dock:
            raise RuntimeError("Repeated launch created a second Aminate dock.")

    theme_rounds = []
    panel = aminate_mobu._QT_TOOL
    for _index in range(6):
        panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
        _process_events(app, 1)
        native_ok = (
            aminate_mobu.get_active_theme() == aminate_mobu.THEME_MOTIONBUILDER
            and aminate_mobu._APP_THEME_OWNED is False
            and _style_pointer(app) == style_pointer
        )
        panel._apply_theme(aminate_mobu.THEME_MODERN)
        _process_events(app, 1)
        modern_ok = (
            aminate_mobu.get_active_theme() == aminate_mobu.THEME_MODERN
            and aminate_mobu._APP_THEME_OWNED is True
        )
        panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
        _process_events(app, 1)
        restored_pointer_ok = _style_pointer(app) == style_pointer
        theme_rounds.append(
            {
                "native_ok": native_ok,
                "modern_ok": modern_ok,
                "restored_style_pointer_unchanged": restored_pointer_ok,
            }
        )
        if not (native_ok and modern_ok and restored_pointer_ok):
            raise RuntimeError("Theme switch did not restore the native Qt style or state.")

    close_reopen = []
    for _index in range(3):
        current = aminate_mobu._QT_DOCK
        current.close()
        _process_events(app)
        closed_ok = (
            aminate_mobu._QT_DOCK is None
            and aminate_mobu._QT_TOOL is None
            and aminate_mobu._APP_THEME_OWNED is False
            and _style_pointer(app) == style_pointer
        )
        reopened = aminate_mobu.launch_aminate_mobu()
        _process_events(app)
        reopened_ok = (
            aminate_mobu._qt_object_is_valid(reopened)
            and aminate_mobu._qt_object_is_valid(aminate_mobu._QT_TOOL)
        )
        close_reopen.append({"closed_ok": closed_ok, "reopened_ok": reopened_ok})
        if not (closed_ok and reopened_ok):
            raise RuntimeError("Dock close/reopen cycle failed.")

    history_rounds = []
    for _index in range(3):
        history = aminate_mobu_history.launch_motionbuilder_history_timeline()
        _process_events(app)
        opened_ok = aminate_mobu_history._qt_object_is_valid(history)
        history.close()
        _process_events(app)
        closed_ok = (
            aminate_mobu_history.GLOBAL_WINDOW is None
            and aminate_mobu_history.GLOBAL_CONTROLLER is None
        )
        history_rounds.append({"opened_ok": opened_ok, "closed_ok": closed_ok})
        if not (opened_ok and closed_ok):
            raise RuntimeError("History close/reopen cycle failed.")

    aminate_mobu._QT_TOOL._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
    _process_events(app)
    docks = aminate_mobu._existing_aminate_mobu_docks()
    toolbars = aminate_mobu._existing_aminate_launcher_toolbars()
    payload = {
        "ok": bool(
            len(docks) == 1
            and len(toolbars) == 1
            and _style_pointer(app) == style_pointer
            and aminate_mobu.get_active_theme() == aminate_mobu.THEME_MOTIONBUILDER
        ),
        "source": aminate_mobu.__file__,
        "build": aminate_mobu.QT_PANEL_BUILD_VERSION,
        "style_pointer": style_pointer,
        "launch_ids": launch_ids,
        "theme_rounds": theme_rounds,
        "close_reopen": close_reopen,
        "history_rounds": history_rounds,
        "dock_count": len(docks),
        "toolbar_count": len(toolbars),
        "final_theme": aminate_mobu.get_active_theme(),
    }
    print("AMINATE_CRASH_GUARDS_RUNTIME " + json.dumps(payload, sort_keys=True))
    if not payload["ok"]:
        raise RuntimeError("Aminate crash-guard runtime proof failed.")
    return payload


run()
