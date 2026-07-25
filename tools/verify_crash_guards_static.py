from __future__ import annotations

import json
import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

FORBIDDEN = {
    "aminate_mobu.py": [
        "app.setStyle(",
        "importlib.reload(aminate_mobu)",
        "destroyed.connect(",
    ],
    "install_motionbuilder_startup.py": [
        "importlib.reload(aminate_mobu)",
    ],
    "launch_aminate_mobu.py": [
        "importlib.reload(aminate_mobu)",
    ],
    "install_aminate_mobu_dragdrop.py": [
        "shutil.rmtree(target_dir)",
    ],
    "tools/capture_default_ui_snapshot.py": [
        "importlib.reload(aminate_mobu)",
    ],
    "tools/verify_easy_tooltips_runtime.py": [
        "importlib.reload(aminate_mobu)",
    ],
}

REQUIRED = {
    "aminate_mobu.py": [
        "QT_PANEL_BUILD_VERSION = 27",
        "def _qt_object_is_valid(value):",
        "QtCore.QTimer.singleShot(0, _restore_app_theme)",
    ],
    "install_aminate_mobu_dragdrop.py": [
        "dirs_exist_ok=True",
        'sys.modules.pop("launch_aminate_mobu", None)',
        "if was_loaded",
    ],
}


def main():
    findings = []
    checked = []
    for relative_path, snippets in FORBIDDEN.items():
        path = REPO_ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        checked.append(relative_path)
        for snippet in snippets:
            if snippet in text:
                findings.append(
                    {
                        "file": relative_path,
                        "kind": "forbidden",
                        "snippet": snippet,
                    }
                )
    for relative_path, snippets in REQUIRED.items():
        path = REPO_ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        if relative_path not in checked:
            checked.append(relative_path)
        for snippet in snippets:
            if snippet not in text:
                findings.append(
                    {
                        "file": relative_path,
                        "kind": "missing_guard",
                        "snippet": snippet,
                    }
                )
    payload = {
        "ok": not findings,
        "checked": checked,
        "findings": findings,
    }
    print("AMINATE_CRASH_GUARDS_STATIC " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
