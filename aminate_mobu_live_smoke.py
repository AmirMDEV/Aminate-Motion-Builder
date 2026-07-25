from __future__ import absolute_import, division, print_function

import json
import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent
RUNNER_CANDIDATES = [
    pathlib.Path(
        r"C:\Users\Amir Mansaray\.agents\skills\motionbuilder-desktop-recipes"
        r"\scripts\run_motionbuilder_python.py"
    ),
    pathlib.Path(
        r"C:\Users\Amir Mansaray\.codex\skills\motionbuilder-desktop-recipes"
        r"\scripts\run_motionbuilder_python.py"
    ),
]
RUNNER = next((path for path in RUNNER_CANDIDATES if path.is_file()), RUNNER_CANDIDATES[0])
REPORT_PATH = REPO_ROOT / "aminate_mobu_live_smoke_report.json"
CHECKS = [
    ("workflow_tabs", "tools/verify_workflow_tabs_runtime.py", "AMINATE_WORKFLOW_TABS "),
    ("core_workflows", "tools/verify_core_workflows_runtime.py", "AMINATE_CORE_WORKFLOWS "),
]


def _run_runtime_check(name, relative_path, marker):
    script_path = REPO_ROOT / relative_path
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--timeout",
            "180",
            "--exec-file",
            str(script_path),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = None
    for line in completed.stdout.splitlines():
        if marker in line:
            payload = json.loads(line.split(marker, 1)[1])
    return {
        "name": name,
        "script": str(script_path),
        "returncode": completed.returncode,
        "payload": payload,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "ok": bool(completed.returncode == 0 and payload and payload.get("ok")),
    }


def main():
    if not RUNNER.is_file():
        raise RuntimeError("MotionBuilder console runner not found: {0}".format(RUNNER))

    results = [
        _run_runtime_check(name, relative_path, marker)
        for name, relative_path, marker in CHECKS
    ]
    report = {
        "ok": all(result["ok"] for result in results),
        "runner": str(RUNNER),
        "repo_root": str(REPO_ROOT),
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote {0}".format(REPORT_PATH))
    print(
        json.dumps(
            {
                "ok": report["ok"],
                "checks": {
                    result["name"]: result["ok"]
                    for result in results
                },
            },
            indent=2,
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
