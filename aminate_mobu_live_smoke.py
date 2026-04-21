from __future__ import absolute_import, division, print_function

import json
import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent
RUNNER = pathlib.Path(r"C:\Users\Amir Mansaray\.codex\skills\motionbuilder-desktop-recipes\scripts\run_motionbuilder_python.py")
MIA_SCENE = pathlib.Path(r"C:\Program Files\Autodesk\MotionBuilder 2026\Tutorials\mia_fk_runstopturn.fbx")
REPORT_PATH = REPO_ROOT / "aminate_mobu_live_smoke_report.json"


def run_lines(lines, settle=0.5):
    command = [
        sys.executable,
        str(RUNNER),
        "--json",
        "--banner-wait",
        "0.25",
        "--settle",
        str(settle),
    ]
    for line in lines:
        command.extend(["--line", line])
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def extract_outputs(payload):
    return [item.get("output", "") for item in payload.get("results", [])]


def main():
    report = {"steps": []}

    bootstrap = run_lines(
        [
            "from pyfbsdk import *",
            "import sys, importlib",
            "repo=r'{0}'".format(str(REPO_ROOT)),
            "sys.path.insert(0, repo) if repo not in sys.path else None",
            "FBApplication().FileOpen(r'{0}')".format(str(MIA_SCENE)),
            "import aminate_mobu",
            "importlib.reload(aminate_mobu)",
            "aminate_mobu.reset_runtime_state(clear_tool=True)",
            "aminate_mobu.launch_aminate_mobu()",
            "print('BOOTSTRAP_OK')",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "bootstrap", "payload": bootstrap})

    singleton = run_lines(
        [
            "from pyfbsdk import *",
            "import sys, importlib",
            "repo=r'{0}'".format(str(REPO_ROOT)),
            "sys.path.insert(0, repo) if repo not in sys.path else None",
            "import aminate_mobu",
            "first=aminate_mobu.launch_aminate_mobu()",
            "importlib.reload(aminate_mobu)",
            "second=aminate_mobu.launch_aminate_mobu()",
            "app=aminate_mobu.QtWidgets.QApplication.instance()",
            "wins=[w for w in app.topLevelWidgets() if getattr(w,'objectName',lambda: '')()==aminate_mobu.QT_WINDOW_OBJECT_NAME]",
            "print('WINDOW_COUNT', len(wins))",
            "print('VISIBLE_COUNT', len([w for w in wins if w.isVisible()]))",
            "print('SAME_WINDOW', first is second)",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "singleton_window", "payload": singleton})

    theme_toggle = run_lines(
        [
            "from pyfbsdk import *",
            "import sys, importlib",
            "repo=r'{0}'".format(str(REPO_ROOT)),
            "sys.path.insert(0, repo) if repo not in sys.path else None",
            "import aminate_mobu",
            "importlib.reload(aminate_mobu)",
            "aminate_mobu.reset_runtime_state(clear_tool=True)",
            "window=aminate_mobu.launch_aminate_mobu()",
            "app=aminate_mobu.QtWidgets.QApplication.instance()",
            "print('THEME_START', window.theme_key)",
            "print('APP_THEME_OWNED_START', aminate_mobu._APP_THEME_OWNED)",
            "print('APP_EQUALS_BASELINE_START', app.styleSheet()==(aminate_mobu._APP_THEME_BASELINE or ''))",
            "window._toggle_theme()",
            "print('THEME_AFTER_FIRST', window.theme_key)",
            "print('APP_THEME_OWNED_AFTER_FIRST', aminate_mobu._APP_THEME_OWNED)",
            "print('APP_EQUALS_MODERN_AFTER_FIRST', app.styleSheet()==aminate_mobu._app_theme_stylesheet(window.theme_key))",
            "window._toggle_theme()",
            "print('THEME_AFTER_SECOND', window.theme_key)",
            "print('APP_THEME_OWNED_AFTER_SECOND', aminate_mobu._APP_THEME_OWNED)",
            "print('APP_EQUALS_BASELINE_AFTER_SECOND', app.styleSheet()==(aminate_mobu._APP_THEME_BASELINE or ''))",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "theme_toggle", "payload": theme_toggle})

    cleaner = run_lines(
        [
            "from pyfbsdk import *",
            "import aminate_mobu",
            "camera=FBCamera('AMINATE_TEST_CAMERA')",
            "marker_drop=FBModelMarker('Marker')",
            "prop_marker_a=FBModelMarker('Marker')",
            "prop_marker_b=FBModelMarker('Marker')",
            "prop_a_translation=prop_marker_a.PropertyList.Find('Lcl Translation')",
            "prop_a_translation.SetAnimated(True)",
            "prop_a_node=prop_a_translation.GetAnimationNode()",
            "(getattr(prop_a_node,'Nodes',[]) or [None])[0].KeyAdd(FBTime(0,0,0,1), 12.5)",
            "prop_b_rotation=prop_marker_b.PropertyList.Find('Lcl Rotation')",
            "prop_b_rotation.SetAnimated(True)",
            "prop_b_node=prop_b_rotation.GetAnimationNode()",
            "(getattr(prop_b_node,'Nodes',[]) or [None])[1].KeyAdd(FBTime(0,0,0,2), 35.0)",
            "marker_keep=FBModelMarker('AMINATE_KEEP_MARKER')",
            "result=aminate_mobu.run_scene_cleaner(prop_marker_base_name='Gun')",
            "print(result)",
            "print('KEEP_MARKER', FBFindModelByLabelName('AMINATE_KEEP_MARKER') is not None)",
            "print('DROP_MARKER', FBFindModelByLabelName('Marker') is not None)",
            "print('OLD_PROP_A', FBFindModelByLabelName('Marker 1') is not None)",
            "print('OLD_PROP_B', FBFindModelByLabelName('Marker 2') is not None)",
            "print('GUN_1', FBFindModelByLabelName('Gun_1') is not None)",
            "print('GUN_2', FBFindModelByLabelName('Gun_2') is not None)",
            "print('DROP_CAMERA', FBFindModelByLabelName('AMINATE_TEST_CAMERA') is not None)",
        ]
    )
    report["steps"].append({"name": "scene_cleaner", "payload": cleaner})

    auto_map = run_lines(
        [
            "from pyfbsdk import *",
            "import aminate_mobu",
            "result=aminate_mobu.auto_map_character(create_control_rig=True, characterize=True, activate_input=False)",
            "print(result)",
            "print('CURRENT_CHAR', FBApplication().CurrentCharacter.LongName if FBApplication().CurrentCharacter else 'NONE')",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "auto_map", "payload": auto_map})

    lock_warning = run_lines(
        [
            "from pyfbsdk import *",
            "import aminate_mobu",
            "aminate_mobu.reset_runtime_state(clear_tool=False)",
            "aminate_mobu.install_runtime_watchers()",
            "result=aminate_mobu.auto_map_character(create_control_rig=False, characterize=False, activate_input=False)",
            "print(result['character_name'])",
            "print(aminate_mobu.validate_current_character())",
            "print(aminate_mobu.get_warning_history())",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "lock_warning", "payload": lock_warning})

    mode_warning = run_lines(
        [
            "from pyfbsdk import *",
            "import aminate_mobu",
            "aminate_mobu.reset_runtime_state(clear_tool=False)",
            "aminate_mobu.install_runtime_watchers()",
            "char=FBSystem().Scene.Characters[0]",
            "FBApplication().CurrentCharacter=char",
            "char.KeyingMode=FBCharacterKeyingMode.kFBCharacterKeyingSelection",
            "model=[char.GetCtrlRigModel(v) for v in FBBodyNodeId.values.values() if char.GetCtrlRigModel(v)][0]",
            "print(aminate_mobu.handle_transform_attempt(model, 'Lcl Rotation'))",
            "print(aminate_mobu.get_warning_history())",
        ],
        settle=0.75,
    )
    report["steps"].append({"name": "mode_warning", "payload": mode_warning})

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote {0}".format(REPORT_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
