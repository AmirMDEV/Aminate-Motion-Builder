from __future__ import annotations
import importlib, json, os, sys
REPO_ROOT = r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder"
if REPO_ROOT not in sys.path: sys.path.insert(0, REPO_ROOT)
import aminate_mobu
aminate_mobu = importlib.reload(aminate_mobu)
dock = aminate_mobu.launch_aminate_mobu()
panel = dock.panel
main = aminate_mobu._qt_host_main_window()
snapshot = json.load(open(aminate_mobu._default_ui_snapshot_path(), "r", encoding="utf-8"))
native_before = bytes(main.saveState().toBase64()).decode("ascii") == snapshot.get("state_b64", "")
native_before
panel._apply_theme(aminate_mobu.THEME_MODERN)
aminate_mobu.get_active_theme()
main.grab().save(r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder\motionbuilder_modern_after_snapshot.png")
os.path.isfile(r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder\motionbuilder_modern_after_snapshot.png")
panel._apply_theme(aminate_mobu.THEME_MOTIONBUILDER)
aminate_mobu.get_active_theme()
restored = bytes(main.saveState().toBase64()).decode("ascii") == snapshot.get("state_b64", "")
restored
main.grab().save(r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder\motionbuilder_restored_from_snapshot.png")
os.path.isfile(r"C:\Users\Amir Mansaray\Documents\Github\Aminate-Motionbuilder\motionbuilder_restored_from_snapshot.png")
