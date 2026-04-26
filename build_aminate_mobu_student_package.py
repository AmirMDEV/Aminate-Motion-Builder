from __future__ import absolute_import, division, print_function

import json
import pathlib
import shutil


REPO_ROOT = pathlib.Path(__file__).resolve().parent
PACKAGE_ROOT = REPO_ROOT / "student_package" / "Aminate_Motion_Builder_Install_Files"
PAYLOAD_ROOT = PACKAGE_ROOT / "install_files"
ZIP_PATH = REPO_ROOT / "student_package" / "Aminate_Motion_Builder_v0.1_BETA.zip"
MANIFEST_FILE_NAME = "manifest.json"
LICENSE_FILE_NAME = "LICENSE"
RELEASE_VERSION_LABEL = "Version 0.1 BETA"
RELEASE_TAG = "v0.1-beta"
PUBLIC_REPO_URL = "https://github.com/AmirMDEV/Aminate-Motion-Builder"
FOLLOW_AMIR_URL = "https://followamir.com"
DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=2U2GXSKFJKJCA"
RUNTIME_FILES = [
    "aminate_mobu.py",
    "aminate_mobu_history.py",
    "install_motionbuilder_startup.py",
    "launch_aminate_mobu.py",
]
DRAG_DROP_INSTALLER = "install_aminate_mobu_dragdrop.py"
DRAG_DROP_INSTALLER_NAME = "Install_Aminate_Motion_Builder.py"
INSTALL_FILES_FOLDER = "install_files"
ASSET_DIRS = [
    "assets",
]


def reset_package_root():
    if not PACKAGE_ROOT.exists():
        return
    try:
        shutil.rmtree(PACKAGE_ROOT)
    except PermissionError:
        # MotionBuilder can hold tutorial GIF previews open. Refresh files in place
        # so code/package updates still ship without forcing the user to close Mobu.
        pass


def build_student_package():
    reset_package_root()
    PAYLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    old_zip_path = REPO_ROOT / "student_package" / "Aminate_Mobu_v0.1_BETA.zip"
    if old_zip_path.exists():
        old_zip_path.unlink()

    for file_name in RUNTIME_FILES:
        shutil.copy2(str(REPO_ROOT / file_name), str(PAYLOAD_ROOT / file_name))
    shutil.copy2(str(REPO_ROOT / DRAG_DROP_INSTALLER), str(PACKAGE_ROOT / DRAG_DROP_INSTALLER_NAME))
    for dir_name in ASSET_DIRS:
        source_dir = REPO_ROOT / dir_name
        if source_dir.exists():
            shutil.copytree(str(source_dir), str(PAYLOAD_ROOT / dir_name), dirs_exist_ok=True)
    shutil.copy2(str(REPO_ROOT / LICENSE_FILE_NAME), str(PAYLOAD_ROOT / LICENSE_FILE_NAME))

    manifest = {
        "package_name": "Aminate Motion Builder",
        "version": RELEASE_VERSION_LABEL,
        "release_tag": RELEASE_TAG,
        "license": "Aminate Proprietary Source-Available License",
        "license_file": LICENSE_FILE_NAME,
        "public_repository": PUBLIC_REPO_URL,
        "follow_amir": FOLLOW_AMIR_URL,
        "donation_url": DONATE_URL,
        "runtime_files": list(RUNTIME_FILES),
        "drag_drop_installer": DRAG_DROP_INSTALLER_NAME,
        "install_files_folder": INSTALL_FILES_FOLDER,
        "asset_dirs": list(ASSET_DIRS),
    }
    with (PAYLOAD_ROOT / MANIFEST_FILE_NAME).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2))
        handle.write("\n")

    readme_lines = [
        "Aminate Motion Builder install files",
        "",
        "Fast install in MotionBuilder:",
        "1. Unzip this package.",
        "2. Open the Aminate_Motion_Builder_Install_Files folder.",
        "3. Drag Install_Aminate_Motion_Builder.py into the MotionBuilder viewport.",
        "4. Aminate installs its startup hook, opens the Aminate panel, and switches to the Modern UI.",
        "",
        "Package layout:",
        "- Main folder: only the drag-and-drop installer file plus the install_files folder.",
        "- install_files: all runtime scripts, assets, license, manifest, and this README.",
        "",
        "Manual fallback:",
        "1. Open Python Tools or the Python Editor in MotionBuilder.",
        "2. Run install_files\\install_motionbuilder_startup.py to install the startup hook.",
        "3. Run install_files\\launch_aminate_mobu.py to open Aminate immediately.",
        "",
        "Current functions:",
        "- Scene Cleaner removes junk scene objects, user cameras, and unused unlabeled markers while preserving useful animated prop markers.",
        "- Auto Map Skeleton reads the selected skeleton, bone, or mesh, creates animate_auto_1, animate_auto_2, etc., and fills a HumanIK character definition.",
        "- T-Pose Frame 0 keys a MotionBuilder-friendly T-pose on frame 0 for retargeting and character-definition cleanup.",
        "- Definition Manager saves, loads, renames, and removes reusable skeleton definitions.",
        "- Constraints Manager lists useful MotionBuilder constraints, explains when to use them, helps rename them, keys them, and opens bake/plot options.",
        "- Prop Take Offset Manager stores selected prop constraint offsets per take so prop setups can survive different prop starting positions.",
        "- History Timeline saves full-scene MotionBuilder snapshots with restore, milestones, branching, snapshot caps, and Auto History.",
        "- Modern UI restyles Aminate and themeable MotionBuilder chrome while keeping the default MotionBuilder UI restore path available.",
        "- Rich tooltips explain buttons and tool icons in plain language.",
        "- Startup install targets all detected MotionBuilder version folders under Documents\\MB.",
        "",
        "Credit: Amir Mansaray",
        "GitHub: {0}".format(PUBLIC_REPO_URL),
        "Follow Amir: {0}".format(FOLLOW_AMIR_URL),
        "Donate: {0}".format(DONATE_URL),
        "Full license: see LICENSE",
    ]
    with (PAYLOAD_ROOT / "README.txt").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(readme_lines))
        handle.write("\n")

    shutil.make_archive(str(ZIP_PATH.with_suffix("")), "zip", str(PACKAGE_ROOT.parent), PACKAGE_ROOT.name)
    return manifest


def main():
    manifest = build_student_package()
    print("Built install files at {0}".format(PACKAGE_ROOT))
    print("Version: {0}".format(manifest["version"]))
    print("Zip: {0}".format(ZIP_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
