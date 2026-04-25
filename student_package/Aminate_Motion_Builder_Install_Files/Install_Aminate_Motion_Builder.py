from __future__ import absolute_import, division, print_function

import os
import shutil
import sys
import traceback


PACKAGE_NAME = "Aminate Motion Builder"
INSTALL_VERSION = "v0.1-beta"
PAYLOAD_FOLDER = "install_files"


def _message(title, text):
    try:
        from pyfbsdk import FBMessageBox

        FBMessageBox(title, text, "OK")
    except Exception:
        print("{0}: {1}".format(title, text))


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _documents_dir():
    return os.path.join(os.path.expanduser("~"), "Documents")


def _payload_dir(package_dir):
    packaged_payload = os.path.join(package_dir, PAYLOAD_FOLDER)
    if os.path.isdir(packaged_payload):
        return packaged_payload
    if os.path.isfile(os.path.join(package_dir, "aminate_mobu.py")):
        return package_dir
    raise RuntimeError(
        "Could not find {0}. Keep Install_Aminate_Motion_Builder.py beside the {0} folder, then drag it into MotionBuilder again.".format(
            PAYLOAD_FOLDER
        )
    )


def _install_dir():
    return os.path.join(_documents_dir(), "MB", "AminateMobu", INSTALL_VERSION)


def _copy_payload(source_dir, target_dir):
    parent_dir = os.path.dirname(target_dir)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)


def install_and_launch():
    package_dir = _script_dir()
    source_dir = _payload_dir(package_dir)
    target_dir = _install_dir()
    _copy_payload(source_dir, target_dir)

    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)

    import install_motionbuilder_startup
    import launch_aminate_mobu

    written = install_motionbuilder_startup.install_motionbuilder_startup()
    launch_aminate_mobu.launch()

    startup_text = "\n".join(written) if written else "No MotionBuilder startup folders were detected."
    _message(
        "Aminate installed",
        "Aminate Motion Builder 0.1 Beta is installed.\n\nStartup hooks:\n{0}\n\nRestart MotionBuilder any time to load Aminate automatically.".format(
            startup_text
        ),
    )
    return target_dir


def main():
    try:
        installed_dir = install_and_launch()
        print("{0} installed to {1}".format(PACKAGE_NAME, installed_dir))
        return 0
    except Exception as exc:
        details = traceback.format_exc()
        _message("Aminate install failed", "{0}\n\n{1}".format(exc, details))
        return 1


if __name__ in ("__main__", "builtins"):
    main()
