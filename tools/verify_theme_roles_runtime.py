import importlib
import json
import os
import sys


REPO = r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder"
REPORT = os.path.join(REPO, "scratch_theme_roles_verify.json")

if REPO not in sys.path:
    sys.path.insert(0, REPO)

import aminate_mobu

aminate_mobu = importlib.reload(aminate_mobu)
panel = aminate_mobu.launch_aminate_mobu()
if hasattr(panel, "panel"):
    panel = panel.panel
app = aminate_mobu._qt_application()

panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
baseline = app.styleSheet() if app is not None else None
native_local = panel.styleSheet()
native_app = app.styleSheet() if app is not None else None
native_owned = getattr(aminate_mobu, "_APP_THEME_OWNED", None)

panel._apply_theme(aminate_mobu.THEME_MODERN)
modern_local = panel.styleSheet()
modern_app = app.styleSheet() if app is not None else None
modern_owned = getattr(aminate_mobu, "_APP_THEME_OWNED", None)

panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
restored_app = app.styleSheet() if app is not None else None
restored_owned = getattr(aminate_mobu, "_APP_THEME_OWNED", None)

payload = {
    "baseline_len": len(baseline or ""),
    "native_local_len": len(native_local or ""),
    "native_app_equals_baseline": native_app == baseline,
    "native_owned": native_owned,
    "modern_local_len": len(modern_local or ""),
    "modern_app_equals_baseline": modern_app == baseline,
    "modern_owned": modern_owned,
    "restored_app_equals_baseline": restored_app == baseline,
    "restored_owned": restored_owned,
}

with open(REPORT, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)

print(REPORT)
