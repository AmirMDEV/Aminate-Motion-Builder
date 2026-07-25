from __future__ import annotations

import json
import os

import aminate_mobu


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(REPO_ROOT, "scratch_theme_roles_verify.json")


def _palette_signature(palette):
    if palette is None:
        return None
    return [
        palette.color(group, role).rgba()
        for group in (
            aminate_mobu.QtGui.QPalette.Active,
            aminate_mobu.QtGui.QPalette.Inactive,
            aminate_mobu.QtGui.QPalette.Disabled,
        )
        for role in (
            aminate_mobu.QtGui.QPalette.Window,
            aminate_mobu.QtGui.QPalette.WindowText,
            aminate_mobu.QtGui.QPalette.Base,
            aminate_mobu.QtGui.QPalette.Text,
            aminate_mobu.QtGui.QPalette.Button,
            aminate_mobu.QtGui.QPalette.ButtonText,
            aminate_mobu.QtGui.QPalette.Highlight,
            aminate_mobu.QtGui.QPalette.HighlightedText,
        )
    ]


app = aminate_mobu._qt_application()
main = aminate_mobu._qt_host_main_window()
panel = aminate_mobu._QT_TOOL
if app is None or main is None or panel is None:
    raise RuntimeError("Aminate and the MotionBuilder Qt host must be open before verification.")

aminate_mobu._sync_baseline_from_app_cache(app)
baseline_stylesheet = aminate_mobu._APP_THEME_BASELINE
baseline_palette = aminate_mobu._copy_palette(aminate_mobu._APP_THEME_BASELINE_PALETTE)
if baseline_stylesheet is None or baseline_palette is None:
    raise RuntimeError("MotionBuilder native theme baseline is unavailable.")

geometry_before = bytes(main.saveGeometry().toBase64()).decode("ascii")
layout_before = bytes(main.saveState().toBase64()).decode("ascii")

panel._apply_theme(aminate_mobu.THEME_MODERN)
modern = {
    "theme": aminate_mobu.get_active_theme(),
    "app_stylesheet_len": len(app.styleSheet() or ""),
    "app_stylesheet_equals_baseline": (app.styleSheet() or "") == (baseline_stylesheet or ""),
    "app_palette_equals_baseline": aminate_mobu._palettes_match(app.palette(), baseline_palette),
    "owned": aminate_mobu._APP_THEME_OWNED,
}

panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
restored = {
    "theme": aminate_mobu.get_active_theme(),
    "app_stylesheet_len": len(app.styleSheet() or ""),
    "app_stylesheet_equals_baseline": (app.styleSheet() or "") == (baseline_stylesheet or ""),
    "app_palette_equals_baseline": aminate_mobu._palettes_match(app.palette(), baseline_palette),
    "palette_signature_equals_baseline": _palette_signature(app.palette())
    == _palette_signature(baseline_palette),
    "owned": aminate_mobu._APP_THEME_OWNED,
    "geometry_unchanged": bytes(main.saveGeometry().toBase64()).decode("ascii") == geometry_before,
    "layout_unchanged": bytes(main.saveState().toBase64()).decode("ascii") == layout_before,
}

payload = {
    "source": os.path.abspath(aminate_mobu.__file__),
    "baseline_stylesheet_len": len(baseline_stylesheet or ""),
    "modern": modern,
    "restored": restored,
}
payload["ok"] = bool(
    modern["theme"] == aminate_mobu.THEME_MODERN
    and not modern["app_stylesheet_equals_baseline"]
    and modern["owned"] is True
    and restored["theme"] == aminate_mobu.THEME_MOTIONBUILDER
    and restored["app_stylesheet_equals_baseline"]
    and restored["app_palette_equals_baseline"]
    and restored["palette_signature_equals_baseline"]
    and restored["owned"] is False
    and restored["geometry_unchanged"]
)

with open(REPORT, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)

print(json.dumps(payload, indent=2))
if not payload["ok"]:
    raise RuntimeError("MotionBuilder native theme restoration verification failed.")
