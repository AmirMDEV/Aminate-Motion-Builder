from __future__ import annotations

import json
import pathlib
import sys
import zipfile


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ZIP_PATH = REPO_ROOT / "student_package" / "Aminate_Motion_Builder_v0.1_BETA.zip"
PACKAGE_ROOT = "Aminate_Motion_Builder_Install_Files"
PAYLOAD_ROOT = PACKAGE_ROOT + "/install_files"
EXPECTED_VERSION = "Version 0.1 BETA"
EXPECTED_TAG = "v0.1-beta"
RUNTIME_FILES = [
    "aminate_mobu.py",
    "aminate_mobu_history.py",
    "install_motionbuilder_startup.py",
    "launch_aminate_mobu.py",
]
FORBIDDEN_SOURCE = [
    "app.setStyle(",
    "importlib.reload(aminate_mobu)",
    "shutil.rmtree(target_dir)",
]


def _decode(archive, name):
    return archive.read(name).decode("utf-8")


def main():
    zip_path = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ZIP_PATH
    findings = []
    compiled = []
    parity = {}

    with zipfile.ZipFile(zip_path, "r") as archive:
        names = [name.replace("\\", "/") for name in archive.namelist()]
        files = [name for name in names if not name.endswith("/")]
        roots = sorted({name.split("/", 1)[0] for name in files})
        if roots != [PACKAGE_ROOT]:
            findings.append({"kind": "root_layout", "value": roots})

        direct_entries = sorted(
            {
                name[len(PACKAGE_ROOT) + 1 :].split("/", 1)[0]
                for name in files
                if name.startswith(PACKAGE_ROOT + "/")
            }
        )
        expected_direct = ["Install_Aminate_Motion_Builder.py", "install_files"]
        if direct_entries != expected_direct:
            findings.append({"kind": "direct_layout", "value": direct_entries})

        manifest_name = PAYLOAD_ROOT + "/manifest.json"
        manifest = json.loads(_decode(archive, manifest_name))
        if manifest.get("version") != EXPECTED_VERSION:
            findings.append({"kind": "manifest_version", "value": manifest.get("version")})
        if manifest.get("release_tag") != EXPECTED_TAG:
            findings.append({"kind": "manifest_tag", "value": manifest.get("release_tag")})
        if manifest.get("runtime_files") != RUNTIME_FILES:
            findings.append({"kind": "manifest_runtime_files", "value": manifest.get("runtime_files")})

        for name in files:
            if not name.lower().endswith(".py"):
                continue
            source = _decode(archive, name)
            try:
                compile(source, name, "exec")
                compiled.append(name)
            except SyntaxError as exc:
                findings.append({"kind": "syntax", "file": name, "error": str(exc)})
            for snippet in FORBIDDEN_SOURCE:
                if snippet in source:
                    findings.append({"kind": "forbidden", "file": name, "snippet": snippet})

        for runtime_file in RUNTIME_FILES:
            packaged_name = PAYLOAD_ROOT + "/" + runtime_file
            matches = archive.read(packaged_name) == (REPO_ROOT / runtime_file).read_bytes()
            parity[runtime_file] = matches
            if not matches:
                findings.append({"kind": "runtime_parity", "file": runtime_file})

        installer_name = PACKAGE_ROOT + "/Install_Aminate_Motion_Builder.py"
        installer_matches = (
            archive.read(installer_name)
            == (REPO_ROOT / "install_aminate_mobu_dragdrop.py").read_bytes()
        )
        parity["Install_Aminate_Motion_Builder.py"] = installer_matches
        if not installer_matches:
            findings.append(
                {
                    "kind": "installer_parity",
                    "file": "Install_Aminate_Motion_Builder.py",
                }
            )

    payload = {
        "ok": not findings,
        "zip": str(zip_path),
        "version": EXPECTED_VERSION,
        "tag": EXPECTED_TAG,
        "compiled_python_files": compiled,
        "source_package_parity": parity,
        "findings": findings,
    }
    print("AMINATE_RELEASE_PACKAGE " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
