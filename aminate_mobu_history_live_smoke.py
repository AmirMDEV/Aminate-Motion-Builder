from __future__ import absolute_import, division, print_function

import json
import pathlib
import shutil
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent
RUNNER = pathlib.Path(r"C:\Users\Amir Mansaray\.codex\skills\motionbuilder-desktop-recipes\scripts\run_motionbuilder_python.py")
SOURCE_SCENE = pathlib.Path(r"C:\Program Files\Autodesk\MotionBuilder 2026\Tutorials\mia_fk_runstopturn.fbx")
TEST_ROOT = REPO_ROOT / "mobu_history_test"
TEST_SCENE = TEST_ROOT / "mia_history_test.fbx"
HISTORY_ROOT = TEST_ROOT / "mia_history_test_aminate_history"
REPORT_PATH = REPO_ROOT / "aminate_mobu_history_live_smoke_report.json"


def run_lines(lines, settle=1.0):
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


def main():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(SOURCE_SCENE), str(TEST_SCENE))
    if HISTORY_ROOT.exists():
        shutil.rmtree(str(HISTORY_ROOT))

    report = {"test_scene": str(TEST_SCENE), "steps": []}

    history_roundtrip = run_lines(
        [
            "from pyfbsdk import *",
            "import importlib, json, sys, time, uuid",
            "repo=r'{0}'".format(str(REPO_ROOT)),
            "sys.path.insert(0, repo) if repo not in sys.path else None",
            "FBApplication().FileOpen(r'{0}', False)".format(str(TEST_SCENE)),
            "import aminate_mobu_history",
            "importlib.reload(aminate_mobu_history)",
            "c=aminate_mobu_history.MotionBuilderHistoryTimelineController()",
            "r1=c.create_snapshot(label='Baseline')",
            "snap1=r1[2]['id'] if r1[0] else ''",
            "probe1='HISTORY_SMOKE_A_' + uuid.uuid4().hex[:6]",
            "FBModelNull(probe1)",
            "r2=c.create_snapshot(label='Add A')",
            "exists_before_restore=bool(FBFindModelByLabelName(probe1))",
            "restore_result=c.restore_snapshot(snap1, save_current_first=False)",
            "exists_after_restore=bool(FBFindModelByLabelName(probe1))",
            "probe2='HISTORY_SMOKE_B_' + uuid.uuid4().hex[:6]",
            "FBModelNull(probe2)",
            "r3=c.create_snapshot(label='Branch B')",
            "manifest=c._load_manifest(c._context())",
            "branch_count=len(manifest['branches'])",
            "c.set_auto_snapshot_enabled(True)",
            "auto_name='HISTORY_AUTO_' + uuid.uuid4().hex[:6]",
            "FBModelNull(auto_name)",
            "time.sleep(2.2)",
            "c._maybe_snapshot_after_action()",
            "time.sleep(2.2)",
            "c._maybe_snapshot_after_action()",
            "manifest2=c._load_manifest(c._context())",
            "auto_count=len([s for s in manifest2['snapshots'] if s.get('auto')])",
            "summary={'baseline_ok':r1[0],'add_ok':r2[0],'branch_ok':r3[0],'restore_ok':restore_result[0],'exists_before_restore':exists_before_restore,'exists_after_restore':exists_after_restore,'branch_count':branch_count,'auto_snapshot_count':auto_count,'snapshot_count':len(manifest2.get('snapshots',[])),'current_snapshot_id':manifest2.get('current_snapshot_id',''),'history_root':c._context().get('history_root','')}",
            "summary",
        ],
        settle=1.0,
    )
    report["steps"].append({"name": "history_roundtrip", "payload": history_roundtrip})

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote {0}".format(REPORT_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
