from __future__ import absolute_import, division, print_function

import json
import pathlib
import shutil


REPO_ROOT = pathlib.Path(__file__).resolve().parent
PACKAGE_ROOT = REPO_ROOT / "student_package" / "aminate_mobu"
PAYLOAD_ROOT = PACKAGE_ROOT / "aminate_mobu_package"
ZIP_PATH = REPO_ROOT / "student_package" / "Aminate_Mobu_v0.1_BETA.zip"
MANIFEST_FILE_NAME = "manifest.json"
LICENSE_FILE_NAME = "LICENSE"
RELEASE_VERSION_LABEL = "Version 0.1 BETA"
RELEASE_TAG = "v0.1-beta"
PUBLIC_REPO_URL = "https://github.com/AmirMDEV/aminate-public"
FOLLOW_AMIR_URL = "https://followamir.com"
DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=2U2GXSKFJKJCA"
RUNTIME_FILES = [
    "aminate_mobu.py",
    "aminate_mobu_history.py",
    "launch_aminate_mobu.py",
]


def build_student_package():
    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    for file_name in RUNTIME_FILES:
        shutil.copy2(str(REPO_ROOT / file_name), str(PAYLOAD_ROOT / file_name))
    shutil.copy2(str(REPO_ROOT / LICENSE_FILE_NAME), str(PAYLOAD_ROOT / LICENSE_FILE_NAME))
    shutil.copy2(str(REPO_ROOT / LICENSE_FILE_NAME), str(PACKAGE_ROOT / LICENSE_FILE_NAME))

    manifest = {
        "package_name": "Aminate Mobu",
        "version": RELEASE_VERSION_LABEL,
        "release_tag": RELEASE_TAG,
        "license": "Aminate Proprietary Source-Available License",
        "license_file": LICENSE_FILE_NAME,
        "public_repository": PUBLIC_REPO_URL,
        "follow_amir": FOLLOW_AMIR_URL,
        "donation_url": DONATE_URL,
        "runtime_files": list(RUNTIME_FILES),
    }
    with (PAYLOAD_ROOT / MANIFEST_FILE_NAME).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2))
        handle.write("\n")

    readme_lines = [
        "Aminate Mobu student package",
        "",
        "How to run in MotionBuilder:",
        "1. Unzip this package.",
        "2. In MotionBuilder open Python Tools or the Python Editor.",
        "3. Run launch_aminate_mobu.py.",
        "4. The Aminate Mobu tool window opens with Scene Cleaner, Auto Map, warning helpers, and a History Timeline launcher.",
        "",
        "Current functions:",
        "- Scene Cleaner deletes user cameras, preserves animated default prop markers, and renames those preserved markers with your chosen base name.",
        "- Auto Map creates a MotionBuilder character from the best skeleton namespace and tries to characterize through fingers, feet, and extra spine links.",
        "- Popup warnings cover unlocked character definitions and wrong control-rig keying mode.",
        "- History Timeline saves full-scene MotionBuilder snapshots beside the current writable FBX scene, supports restore, milestones, branching, snapshot caps, and Auto History.",
        "",
        "Credit: Amir Mansaray",
        "GitHub: {0}".format(PUBLIC_REPO_URL),
        "Follow Amir: {0}".format(FOLLOW_AMIR_URL),
        "Donate: {0}".format(DONATE_URL),
        "Full license: see LICENSE",
    ]
    with (PACKAGE_ROOT / "README.txt").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(readme_lines))
        handle.write("\n")

    shutil.make_archive(str(ZIP_PATH.with_suffix("")), "zip", str(PACKAGE_ROOT.parent), PACKAGE_ROOT.name)
    return manifest


def main():
    manifest = build_student_package()
    print("Built student package at {0}".format(PACKAGE_ROOT))
    print("Version: {0}".format(manifest["version"]))
    print("Zip: {0}".format(ZIP_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
