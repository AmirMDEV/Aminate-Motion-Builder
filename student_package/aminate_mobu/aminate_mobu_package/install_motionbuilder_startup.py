from __future__ import absolute_import, division, print_function

from pathlib import Path


STARTUP_BOOTSTRAP_FILENAME = "aminate_mobu_startup.py"
MODULE_ROOT = Path(__file__).resolve().parent
MB_DOCUMENTS_ROOT = Path.home() / "Documents" / "MB"


def discover_motionbuilder_startup_dirs(root_dir=None):
    root_dir = Path(root_dir or MB_DOCUMENTS_ROOT)
    if not root_dir.exists():
        return []
    startup_dirs = []
    for child in sorted(root_dir.iterdir(), reverse=True):
        if not child.is_dir():
            continue
        if not child.name.isdigit():
            continue
        startup_dirs.append(child / "config" / "PythonStartup")
    return startup_dirs


def install_motionbuilder_startup():
    target_dirs = discover_motionbuilder_startup_dirs()
    if not target_dirs:
        target_dirs = [MB_DOCUMENTS_ROOT / "2026" / "config" / "PythonStartup"]
    bootstrap = """from __future__ import absolute_import, division, print_function
import importlib
import sys
MODULE_ROOT = r\"{module_root}\"
if MODULE_ROOT not in sys.path:
    sys.path.insert(0, MODULE_ROOT)
def _boot():
    import aminate_mobu
    importlib.reload(aminate_mobu)
    aminate_mobu.launch_aminate_mobu()
try:
    from PySide6 import QtCore
except Exception:
    try:
        from PySide2 import QtCore
    except Exception:
        QtCore = None
if QtCore is not None:
    QtCore.QTimer.singleShot(250, _boot)
else:
    _boot()
""".format(module_root=str(MODULE_ROOT).replace("\\", "\\\\"))
    written = []
    for target_dir in target_dirs:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / STARTUP_BOOTSTRAP_FILENAME
        target_path.write_text(bootstrap, encoding="utf-8")
        written.append(target_path)
    return written


if __name__ == "__main__":
    for path in install_motionbuilder_startup():
        print(path)
