from __future__ import absolute_import, division, print_function

import json
import os
import sys
import time

from pyfbsdk import (
    FBApplication,
    FBCharacterKeyingMode,
    FBFindModelByLabelName,
    FBModelList,
    FBModelMarker,
    FBModelSkeleton,
    FBCamera,
    FBGetSelectedModels,
    FBSystem,
    FBTime,
)

try:
    from PySide6 import QtTest
except Exception:
    from PySide2 import QtTest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIA_SCENE = r"C:\Program Files\Autodesk\MotionBuilder 2026\Tutorials\mia_fk_runstopturn.fbx"


def _click_button(aminate_mobu, panel, tab_index, caption):
    panel.workflow_tabs.setCurrentIndex(tab_index)
    app = aminate_mobu.QtWidgets.QApplication.instance()
    app.processEvents()
    page = panel.workflow_tabs.currentWidget()
    matches = [
        button
        for button in page.findChildren(aminate_mobu.QtWidgets.QPushButton)
        if str(button.text()) == caption
    ]
    if len(matches) != 1:
        raise AssertionError(
            "Expected one {0} button on tab {1}; found {2}".format(
                caption,
                tab_index,
                len(matches),
            )
        )
    button = matches[0]
    if not button.isEnabled() or not button.isVisible():
        raise AssertionError("Button is not usable: {0}".format(caption))
    if hasattr(page, "ensureWidgetVisible"):
        page.ensureWidgetVisible(button, 6, 6)
        app.processEvents()
    QtTest.QTest.mouseClick(
        button,
        aminate_mobu.QtCore.Qt.LeftButton,
        aminate_mobu.QtCore.Qt.NoModifier,
        button.rect().center(),
    )
    app.processEvents()
    return button


def _load_exact_plugin():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    old_module = sys.modules.get("aminate_mobu")
    if old_module is not None:
        try:
            old_module.reset_runtime_state(clear_tool=True)
            old_module.QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    sys.modules.pop("aminate_mobu", None)
    import aminate_mobu

    if os.path.normcase(os.path.abspath(aminate_mobu.__file__)) != os.path.normcase(
        os.path.join(REPO_ROOT, "aminate_mobu.py")
    ):
        raise RuntimeError("Wrong Aminate source loaded: {0}".format(aminate_mobu.__file__))
    aminate_mobu.launch_aminate_mobu()
    return aminate_mobu


def run():
    app = FBApplication()
    current_scene = os.path.normcase(os.path.abspath(app.FBXFileName or ""))
    expected_scene = os.path.normcase(os.path.abspath(MIA_SCENE))
    if current_scene != expected_scene:
        raise RuntimeError(
            "Open the Mia tutorial scene before running the live workflow audit. "
            "Current scene: {0}".format(app.FBXFileName or "Untitled")
        )

    import aminate_mobu

    expected_source = os.path.join(REPO_ROOT, "aminate_mobu.py")
    if os.path.normcase(os.path.abspath(aminate_mobu.__file__)) != os.path.normcase(expected_source):
        aminate_mobu = _load_exact_plugin()
    else:
        aminate_mobu.launch_aminate_mobu()
    qt_app = aminate_mobu.QtWidgets.QApplication.instance()
    panel = aminate_mobu._QT_TOOL
    if panel is None:
        raise RuntimeError("Aminate Qt panel did not launch.")

    checks = {}
    details = {}
    created_models = []
    history_window = None
    definition_names = []
    try:
        camera = FBCamera("AMINATE_TAB_AUDIT_CAMERA")
        marker_drop = FBModelMarker("Marker")
        prop_marker_a = FBModelMarker("Marker")
        prop_marker_b = FBModelMarker("Marker")
        marker_keep = FBModelMarker("AMINATE_TAB_AUDIT_KEEP")
        created_models.extend([prop_marker_a, prop_marker_b, marker_keep])

        prop_a_translation = prop_marker_a.PropertyList.Find("Lcl Translation")
        prop_a_translation.SetAnimated(True)
        prop_a_node = prop_a_translation.GetAnimationNode()
        (getattr(prop_a_node, "Nodes", []) or [None])[0].KeyAdd(FBTime(0, 0, 0, 1), 12.5)

        prop_b_rotation = prop_marker_b.PropertyList.Find("Lcl Rotation")
        prop_b_rotation.SetAnimated(True)
        prop_b_node = prop_b_rotation.GetAnimationNode()
        (getattr(prop_b_node, "Nodes", []) or [None])[1].KeyAdd(FBTime(0, 0, 0, 2), 35.0)

        panel.prop_marker_base_field.setText("AuditProp")
        _click_button(aminate_mobu, panel, 0, "Scene Cleaner")
        prop_a_name = str(prop_marker_a.LongName)
        prop_b_name = str(prop_marker_b.LongName)
        cleaner_state = {
            "camera_deleted": FBFindModelByLabelName("AMINATE_TAB_AUDIT_CAMERA") is None,
            "junk_marker_deleted": FBFindModelByLabelName("Marker") is None,
            "prop_1_preserved": bool(
                prop_a_name.startswith("AuditProp_")
                and FBFindModelByLabelName(prop_a_name) is not None
            ),
            "prop_2_preserved": bool(
                prop_b_name.startswith("AuditProp_")
                and prop_b_name != prop_a_name
                and FBFindModelByLabelName(prop_b_name) is not None
            ),
            "named_marker_preserved": FBFindModelByLabelName("AMINATE_TAB_AUDIT_KEEP") is not None,
            "prop_names": [prop_a_name, prop_b_name],
        }
        checks["scene_cleanup"] = all(
            value
            for key, value in cleaner_state.items()
            if key != "prop_names"
        )
        details["scene_cleanup"] = cleaner_state

        selected = FBModelList()
        FBGetSelectedModels(selected)
        for model in selected:
            model.Selected = False
        skeletons = [
            component
            for component in FBSystem().Scene.Components
            if isinstance(component, FBModelSkeleton)
        ]
        if not skeletons:
            raise AssertionError("Mia scene contains no skeleton models.")
        skeletons[0].Selected = True
        FBSystem().Scene.Evaluate()
        _click_button(aminate_mobu, panel, 1, "Use Selected Skeleton")
        _click_button(aminate_mobu, panel, 1, "Auto Map Skeleton")
        scope_label = aminate_mobu.selected_skeleton_scope_label()
        character = FBApplication().CurrentCharacter
        mapped_ok = bool(
            character
            and character.GetCharacterize()
            and aminate_mobu._core_link_count(character) == len(aminate_mobu.CORE_REQUIRED_LINKS)
        )
        _click_button(aminate_mobu, panel, 1, "Validate Character")
        _click_button(aminate_mobu, panel, 1, "T-Pose Frame 0")
        checks["hik_mapping"] = bool(mapped_ok and scope_label != "No skeleton selected")
        details["hik_mapping"] = {
            "scope": scope_label,
            "character": character.LongName if character else "",
            "characterized": bool(character and character.GetCharacterize()),
            "core_links": aminate_mobu._core_link_count(character) if character else 0,
            "tpose_status": any("T-pose" in line or "T-Pose" in line for line in aminate_mobu._STATUS_LINES),
        }

        if character:
            character.CreateControlRig(True)
        control_rig_created = bool(character and character.GetCurrentControlSet())
        character.KeyingMode = FBCharacterKeyingMode.kFBCharacterKeyingSelection
        rig_models = [
            character.GetCtrlRigModel(value)
            for value in aminate_mobu.FBBodyNodeId.values.values()
            if character.GetCtrlRigModel(value)
        ]
        aminate_mobu._WARNING_LAST_SHOWN["control_rig_mode"] = 0.0
        mode_warning = bool(
            control_rig_created
            and rig_models
            and aminate_mobu.handle_transform_attempt(rig_models[0], "Lcl Rotation")
        )

        aminate_mobu._WARNING_LAST_SHOWN["lock_definition"] = 0.0
        unlocked = aminate_mobu.auto_map_character(
            create_control_rig=False,
            characterize=False,
            activate_input=False,
        )
        _click_button(aminate_mobu, panel, 2, "Check Setup Now")
        warning_kinds = [item.get("kind") for item in aminate_mobu.get_warning_history()]
        warning_text = panel.warning_history_memo.toPlainText()
        _click_button(aminate_mobu, panel, 2, "Body Part Mode")
        body_part_mode = character.KeyingMode == FBCharacterKeyingMode.kFBCharacterKeyingBodyPart
        _click_button(aminate_mobu, panel, 2, "Full Body Mode")
        full_body_mode = character.KeyingMode == FBCharacterKeyingMode.kFBCharacterKeyingFullBody
        warnings_ok = all(
            [
                mode_warning,
                bool(unlocked.get("ok")),
                "lock_definition" in warning_kinds,
                "control_rig_mode" in warning_kinds,
                "lock_definition" in warning_text,
                "control_rig_mode" in warning_text,
                body_part_mode,
                full_body_mode,
            ]
        )
        checks["setup_warnings"] = warnings_ok
        details["setup_warnings"] = {
            "kinds": warning_kinds,
            "history_text": warning_text,
            "body_part_mode": body_part_mode,
            "full_body_mode": full_body_mode,
        }

        definition_base = "CodexTabAudit_{0}".format(int(time.time()))
        definition_renamed = definition_base + "_Renamed"
        definition_names.extend([definition_base, definition_renamed])
        panel.workflow_tabs.setCurrentIndex(1)
        panel.definition_name_field.setText(definition_base)
        _click_button(aminate_mobu, panel, 1, "Save Definition")
        saved = definition_base in aminate_mobu._definition_names()
        panel.definition_combo.setCurrentText(definition_base)
        panel.definition_name_field.setText(definition_renamed)
        _click_button(aminate_mobu, panel, 1, "Rename Definition")
        renamed = (
            definition_renamed in aminate_mobu._definition_names()
            and definition_base not in aminate_mobu._definition_names()
        )
        panel.definition_combo.setCurrentText(definition_renamed)
        _click_button(aminate_mobu, panel, 1, "Delete Definition")
        deleted = definition_renamed not in aminate_mobu._definition_names()
        checks["definitions"] = bool(saved and renamed and deleted)
        details["definitions"] = {"saved": saved, "renamed": renamed, "deleted": deleted}

        _click_button(aminate_mobu, panel, 3, "List Constraints")
        constraint_rows = aminate_mobu.constraint_rows()
        constraints_ok = panel.constraints_table.rowCount() == len(constraint_rows)
        checks["constraints"] = constraints_ok
        details["constraints"] = {
            "table_rows": panel.constraints_table.rowCount(),
            "scene_rows": len(constraint_rows),
        }

        sys.modules.pop("aminate_mobu_history", None)
        _click_button(aminate_mobu, panel, 4, "History Timeline")
        history_error = ""
        history_module = sys.modules.get("aminate_mobu_history")
        history_window = getattr(history_module, "GLOBAL_WINDOW", None) if history_module else None
        if history_window is None:
            try:
                aminate_mobu._on_history_timeline()
            except Exception as exc:
                history_error = "{0}: {1}".format(type(exc).__name__, exc)
            history_module = sys.modules.get("aminate_mobu_history")
            history_window = getattr(history_module, "GLOBAL_WINDOW", None) if history_module else None
        history_ok = bool(
            history_window
            and history_window.isVisible()
            and history_window.windowTitle() == "Aminate Mobu History Timeline"
        )
        checks["history"] = history_ok
        details["history"] = {
            "visible": bool(history_window and history_window.isVisible()),
            "title": history_window.windowTitle() if history_window else "",
            "error": history_error,
            "status_tail": list(aminate_mobu._STATUS_LINES[-5:]),
        }

        checks["all_workflows"] = all(checks.values())
    finally:
        for name in definition_names:
            try:
                if name in aminate_mobu._definition_names():
                    aminate_mobu.delete_character_definition(name)
            except Exception:
                pass
        for model in created_models:
            try:
                model.FBDelete()
            except Exception:
                pass
        try:
            panel.workflow_tabs.setCurrentIndex(0)
            qt_app.processEvents()
        except Exception:
            pass

    payload = {
        "ok": bool(checks.get("all_workflows")),
        "source": os.path.abspath(aminate_mobu.__file__),
        "build": panel._build_version,
        "scene": FBApplication().FBXFileName,
        "checks": checks,
        "details": details,
        "dock_width": aminate_mobu._QT_DOCK.width(),
    }
    print("AMINATE_CORE_WORKFLOWS " + json.dumps(payload, sort_keys=True))
    return payload


run()
