from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import time
import uuid

from pyfbsdk import (
    FBApplication,
    FBCharacter,
    FBCamera,
    FBComponent,
    FBModel,
    FBModelMarker,
    FBModelMarkerOptical,
    FBPlayerControl,
    FBStringList,
    FBSystem,
)

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except Exception:  # pragma: no cover - MotionBuilder fallback
    QtCore = None
    QtGui = None
    QtWidgets = None

try:
    import pyfbsdk_additions
except Exception:  # pragma: no cover - MotionBuilder fallback
    pyfbsdk_additions = None


WINDOW_OBJECT_NAME = "aminateMobuHistoryTimelineWindow"
MANIFEST_FILE_NAME = "history_manifest.json"
SNAPSHOT_FOLDER_NAME = "snapshots"
MANIFEST_VERSION = 1
AMINATE_MOBU_HISTORY_VERSION = "0.1"
DEFAULT_SNAPSHOT_CAP = 50
DEFAULT_STEP_COLOR = "#4CC9F0"
DEFAULT_MILESTONE_COLOR = "#F6C85F"
DEFAULT_AUTO_COLOR = "#8D99AE"
AUTO_SNAPSHOT_SETTLE_SECONDS = 1.5
AUTO_SNAPSHOT_INTERVAL_MS = 2000
AUTO_SNAPSHOT_MODE_ALL = "all"
AUTO_SNAPSHOT_MODE_CUSTOM = "custom"
DEFAULT_AUTO_SNAPSHOT_ENABLED = False
DEFAULT_AUTO_SNAPSHOT_MODE = AUTO_SNAPSHOT_MODE_ALL
AUTO_SNAPSHOT_TRIGGER_LABELS = (
    ("keyframes", "After key edits or plotting"),
    ("constraints", "After constraint changes"),
    ("nodes", "After creating or deleting scene items"),
    ("animation_layers", "After animation layer changes"),
    ("parenting", "After hierarchy changes"),
    ("takes", "After take changes"),
    ("transforms", "After transform-only edits"),
)
DEFAULT_AUTO_SNAPSHOT_TRIGGERS = {
    "keyframes": True,
    "constraints": True,
    "nodes": True,
    "animation_layers": True,
    "parenting": True,
    "takes": True,
    "transforms": True,
}
BRANCH_COLOR_PALETTE = (
    "#4CC9F0",
    "#F76E6E",
    "#7BD88F",
    "#B86BFF",
    "#F4A261",
    "#2EC4B6",
    "#FF5D8F",
    "#9DDBAD",
)
MAX_TABLE_ROWS = 500
MAX_STRIP_MARKERS = 120
TRANSFORM_PROPERTY_NAMES = ("Lcl Translation", "Lcl Rotation", "Lcl Scaling")
CONSTRAINT_PROPERTY_NAMES = ("Weight", "Active")

GLOBAL_CONTROLLER = None
GLOBAL_WINDOW = None
HISTORY_UI_WIDGETS = []
FB_TOOL_NAMES_TO_CLOSE_ON_RESTORE = ("Aminate Mobu",)


def _now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def _safe_name(value, fallback="snapshot"):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip())
    cleaned = cleaned.strip("._")
    return cleaned[:48] or fallback


def _qt_main_window():
    if QtWidgets is None:
        return None
    app = QtWidgets.QApplication.instance()
    if app is None:
        return None
    active = app.activeWindow()
    if active is not None:
        return active
    for widget in app.topLevelWidgets():
        title = widget.windowTitle() or ""
        if "MotionBuilder" in title:
            return widget
    widgets = app.topLevelWidgets()
    return widgets[0] if widgets else None


def _component_long_name(component):
    if component is None:
        return ""
    return str(getattr(component, "LongName", "") or getattr(component, "Name", "") or "")


def _short_name_from_long_name(long_name):
    text = str(long_name or "")
    if ":" not in text:
        return text.split("|")[-1]
    return text.split(":")[-1].split("|")[-1]


def _vector_to_tuple(value):
    try:
        return tuple(round(float(item), 5) for item in value)
    except Exception:
        return ()


def _format_bytes(byte_count):
    amount = float(byte_count or 0)
    units = ("B", "KB", "MB", "GB")
    index = 0
    while amount >= 1024.0 and index < len(units) - 1:
        amount /= 1024.0
        index += 1
    if index == 0:
        return "{0:.0f} {1}".format(amount, units[index])
    return "{0:.1f} {1}".format(amount, units[index])


def _join_preview(values, limit=6):
    items = [str(item) for item in values if str(item).strip()]
    if not items:
        return ""
    preview = items[:limit]
    if len(items) > limit:
        preview.append("+{0} more".format(len(items) - limit))
    return ", ".join(preview)


def _snapshot_file_size(record):
    snapshot_path = record.get("snapshot_path", "")
    if snapshot_path and os.path.exists(snapshot_path):
        try:
            return int(os.path.getsize(snapshot_path))
        except Exception:
            return 0
    return int(record.get("snapshot_size_bytes") or 0)


def _manifest_storage_size(manifest):
    total = 0
    for record in manifest.get("snapshots") or []:
        total += _snapshot_file_size(record)
    return total


def _hash_payload(payload):
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8", errors="replace")
    return hashlib.sha1(encoded).hexdigest()


def _history_root_for_scene(scene_path):
    scene_path = os.path.abspath(scene_path)
    scene_dir = os.path.dirname(scene_path)
    base = os.path.splitext(os.path.basename(scene_path))[0]
    history_root = os.path.join(scene_dir, "{0}_aminate_history".format(base))
    return {
        "scene_path": scene_path,
        "scene_dir": scene_dir,
        "scene_base": base,
        "history_root": history_root,
        "snapshot_dir": os.path.join(history_root, SNAPSHOT_FOLDER_NAME),
        "manifest_path": os.path.join(history_root, MANIFEST_FILE_NAME),
    }


def _infer_original_scene_from_snapshot_path(scene_path):
    if not scene_path:
        return ""
    scene_path = os.path.abspath(scene_path)
    snapshot_dir = os.path.dirname(scene_path)
    history_root = os.path.dirname(snapshot_dir)
    if os.path.basename(snapshot_dir) != SNAPSHOT_FOLDER_NAME:
        return ""
    if not os.path.basename(history_root).endswith("_aminate_history"):
        return ""
    manifest_path = os.path.join(history_root, MANIFEST_FILE_NAME)
    if not os.path.exists(manifest_path):
        return ""
    try:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except Exception:
        return ""
    original_scene_path = manifest.get("original_scene_path", "")
    if original_scene_path:
        return os.path.abspath(original_scene_path)
    return ""


def _register_history_widget(widget):
    if widget not in HISTORY_UI_WIDGETS:
        HISTORY_UI_WIDGETS.append(widget)


def _unregister_history_widget(widget):
    if widget in HISTORY_UI_WIDGETS:
        HISTORY_UI_WIDGETS.remove(widget)


def _notify_history_ui_changed():
    for widget in list(HISTORY_UI_WIDGETS):
        try:
            widget.refresh()
        except Exception:
            pass


def _suspend_history_widgets():
    states = []
    for widget in list(HISTORY_UI_WIDGETS):
        window = None
        try:
            window = widget.window()
        except Exception:
            window = None
        if window is None:
            continue
        state = {"widget": widget, "window": window, "was_visible": bool(window.isVisible())}
        states.append(state)
        try:
            window.hide()
        except Exception:
            pass
    if QtWidgets is not None:
        try:
            QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    return states


def _resume_history_widgets(states):
    if QtWidgets is not None:
        try:
            QtWidgets.QApplication.processEvents()
        except Exception:
            pass
    for state in states or []:
        widget = state.get("widget")
        window = state.get("window")
        if widget is None or window is None:
            continue
        try:
            widget.refresh()
        except Exception:
            pass
        if state.get("was_visible"):
            try:
                window.show()
            except Exception:
                pass


def _close_known_fb_tools_for_restore():
    if pyfbsdk_additions is None:
        return []
    closed = []
    for tool_name in FB_TOOL_NAMES_TO_CLOSE_ON_RESTORE:
        try:
            if tool_name in pyfbsdk_additions.FBToolList:
                pyfbsdk_additions.FBDestroyToolByName(tool_name)
                closed.append(tool_name)
        except Exception:
            pass
    return closed


def _shutdown_aminate_mobu_runtime_for_restore():
    aminate_mobu = sys.modules.get("aminate_mobu")
    if aminate_mobu is None:
        return False
    try:
        aminate_mobu.remove_runtime_watchers()
    except Exception:
        pass
    try:
        aminate_mobu.reset_runtime_state(clear_tool=True)
    except Exception:
        pass
    return True


def snapshots_has_future(manifest, snapshot_id, branch_id=None):
    ordered = list(manifest.get("snapshots") or [])
    index = -1
    for offset, record in enumerate(ordered):
        if record.get("id") == snapshot_id:
            index = offset
            break
    if index < 0:
        return False
    for record in ordered[index + 1 :]:
        if branch_id and record.get("branch_id") != branch_id:
            continue
        return True
    return False


class MotionBuilderHistoryTimelineController(object):
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self._action_timer = None
        self._auto_snapshot_busy = False
        self._pending_summary = None
        self._pending_action_time = 0.0
        self._last_action_summary = None
        self._restored_summary = None
        self._restore_settle_until = 0.0
        self._suppress_until = 0.0

    def set_status_callback(self, callback):
        self.status_callback = callback

    def shutdown(self):
        self.stop_default_action_snapshots()

    def _emit_status(self, message, success=True):
        if callable(self.status_callback):
            try:
                self.status_callback(str(message), bool(success))
                return
            except Exception:
                pass
        print("[Aminate Mobu History] {0}".format(message))

    def _suppress_auto_snapshots_for(self, seconds=2.0):
        self._suppress_until = max(self._suppress_until, time.time() + float(seconds or 0.0))

    def _auto_snapshots_are_suppressed(self):
        return time.time() < self._suppress_until

    def _current_scene_path(self):
        return str(FBApplication().FBXFileName or "").strip()

    def _context(self):
        scene_path = self._current_scene_path()
        if not scene_path:
            return {"ok": False, "message": "Open a saved MotionBuilder FBX scene first."}
        scene_path = os.path.abspath(scene_path)
        original_scene_path = _infer_original_scene_from_snapshot_path(scene_path) or scene_path
        roots = _history_root_for_scene(original_scene_path)
        scene_dir = roots["scene_dir"]
        if not os.path.isdir(scene_dir):
            return {"ok": False, "message": "Scene folder is missing."}
        if not os.access(scene_dir, os.W_OK):
            return {
                "ok": False,
                "message": "Current scene folder is not writable. Save or export the scene to a writable location first.",
            }
        roots["ok"] = True
        roots["current_scene_path"] = scene_path
        roots["original_scene_path"] = original_scene_path
        return roots

    def _default_manifest(self, context):
        return {
            "version": MANIFEST_VERSION,
            "aminate_mobu_history_version": AMINATE_MOBU_HISTORY_VERSION,
            "original_scene_path": context.get("original_scene_path", ""),
            "current_snapshot_id": "",
            "active_branch_id": "main",
            "snapshot_cap": DEFAULT_SNAPSHOT_CAP,
            "auto_snapshot_enabled": DEFAULT_AUTO_SNAPSHOT_ENABLED,
            "auto_snapshot_mode": DEFAULT_AUTO_SNAPSHOT_MODE,
            "auto_snapshot_triggers": dict(DEFAULT_AUTO_SNAPSHOT_TRIGGERS),
            "branches": {
                "main": {
                    "id": "main",
                    "label": "Main",
                    "color": BRANCH_COLOR_PALETTE[0],
                    "parent_id": "",
                    "index": 0,
                }
            },
            "snapshots": [],
            "events": [],
            "snapshot_count": 0,
            "history_storage_size_bytes": 0,
            "updated_at": _now_iso(),
        }

    def _load_manifest(self, context):
        manifest_path = context["manifest_path"]
        if not os.path.exists(manifest_path):
            return self._default_manifest(context)
        try:
            with open(manifest_path, "r", encoding="utf-8") as handle:
                manifest = json.load(handle)
        except Exception:
            manifest = self._default_manifest(context)
        manifest.setdefault("version", MANIFEST_VERSION)
        manifest.setdefault("aminate_mobu_history_version", AMINATE_MOBU_HISTORY_VERSION)
        manifest.setdefault("original_scene_path", context.get("original_scene_path", ""))
        manifest.setdefault("current_snapshot_id", "")
        manifest.setdefault("active_branch_id", "main")
        manifest.setdefault("snapshot_cap", DEFAULT_SNAPSHOT_CAP)
        manifest.setdefault("auto_snapshot_enabled", DEFAULT_AUTO_SNAPSHOT_ENABLED)
        manifest.setdefault("auto_snapshot_mode", DEFAULT_AUTO_SNAPSHOT_MODE)
        manifest.setdefault("auto_snapshot_triggers", dict(DEFAULT_AUTO_SNAPSHOT_TRIGGERS))
        manifest.setdefault("branches", self._default_manifest(context)["branches"])
        manifest.setdefault("snapshots", [])
        manifest.setdefault("events", [])
        self._ensure_branch_records(manifest)
        return manifest

    def _save_manifest(self, context, manifest):
        if not os.path.isdir(context["history_root"]):
            os.makedirs(context["history_root"])
        if not os.path.isdir(context["snapshot_dir"]):
            os.makedirs(context["snapshot_dir"])
        manifest["original_scene_path"] = context.get("original_scene_path", "")
        manifest["snapshot_count"] = len(manifest.get("snapshots") or [])
        manifest["history_storage_size_bytes"] = _manifest_storage_size(manifest)
        manifest["updated_at"] = _now_iso()
        with open(context["manifest_path"], "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")

    def _ensure_branch_records(self, manifest):
        branches = manifest.setdefault("branches", {})
        if "main" not in branches:
            branches["main"] = {
                "id": "main",
                "label": "Main",
                "color": BRANCH_COLOR_PALETTE[0],
                "parent_id": "",
                "index": 0,
            }
        next_index = 1
        for record in branches.values():
            if record.get("id") == "main":
                record.setdefault("label", "Main")
                record.setdefault("color", BRANCH_COLOR_PALETTE[0])
                record.setdefault("index", 0)
                continue
            if not record.get("index"):
                record["index"] = next_index
            next_index = max(next_index, int(record.get("index") or 0) + 1)
            record.setdefault("label", "Branch {0}".format(record["index"]))
            record.setdefault("color", self._branch_color_from_id(record.get("id"), record.get("index")))
        for record in manifest.get("snapshots") or []:
            branch_id = record.get("branch_id") or "main"
            branch = branches.setdefault(
                branch_id,
                {
                    "id": branch_id,
                    "label": "Branch",
                    "color": self._branch_color_from_id(branch_id, len(branches)),
                    "parent_id": "",
                    "index": len(branches),
                },
            )
            record.setdefault("branch_label", branch.get("label"))
            record.setdefault("branch_color", branch.get("color"))

    def _branch_color_from_id(self, branch_id, index=0):
        if branch_id == "main":
            return BRANCH_COLOR_PALETTE[0]
        seed = sum(ord(char) for char in str(branch_id or "main")) + int(index or 0)
        return BRANCH_COLOR_PALETTE[seed % len(BRANCH_COLOR_PALETTE)]

    def _branch_record(self, manifest, branch_id):
        self._ensure_branch_records(manifest)
        branch_id = branch_id or "main"
        branches = manifest.setdefault("branches", {})
        if branch_id not in branches:
            index = max(int(item.get("index") or 0) for item in branches.values()) + 1
            branches[branch_id] = {
                "id": branch_id,
                "label": "Branch {0}".format(index),
                "color": self._branch_color_from_id(branch_id, index),
                "parent_id": "",
                "index": index,
            }
        return branches[branch_id]

    def _create_branch(self, manifest, parent_id):
        branches = manifest.setdefault("branches", {})
        index = max(int(item.get("index") or 0) for item in branches.values()) + 1
        branch_id = "branch_{0}_{1}".format(index, uuid.uuid4().hex[:4])
        branches[branch_id] = {
            "id": branch_id,
            "label": "Branch {0}".format(index),
            "color": self._branch_color_from_id(branch_id, index),
            "parent_id": parent_id or "",
            "index": index,
        }
        manifest["active_branch_id"] = branch_id
        manifest.setdefault("events", []).append(
            {"type": "branch_create", "branch_id": branch_id, "parent_id": parent_id or "", "timestamp": _now_iso()}
        )
        return branch_id

    def _snapshot_for_id(self, manifest, snapshot_id):
        for record in manifest.get("snapshots") or []:
            if record.get("id") == snapshot_id:
                return record
        return None

    def _player_frame(self):
        try:
            return int(FBPlayerControl().GetEditCurrentTime().GetFrame())
        except Exception:
            try:
                return int(FBSystem().LocalTime.GetFrame())
            except Exception:
                return 0

    def _fcurve_digest(self, fcurve):
        if fcurve is None:
            return ""
        key_count = 0
        digest = hashlib.sha1()
        try:
            key_count = len(fcurve.Keys)
        except Exception:
            key_count = 0
        for index in range(key_count):
            try:
                frame = int(fcurve.KeyGetTime(index).GetFrame())
                value = round(float(fcurve.KeyGetValue(index)), 5)
                digest.update("{0}:{1}|".format(frame, value).encode("utf-8"))
            except Exception:
                digest.update("x|".encode("utf-8"))
        return "{0}:{1}".format(key_count, digest.hexdigest())

    def _property_animation_digest(self, prop):
        if prop is None:
            return ""
        try:
            animation_node = prop.GetAnimationNode()
        except Exception:
            animation_node = None
        if animation_node is None:
            return ""
        parts = []
        for child in getattr(animation_node, "Nodes", []) or []:
            fcurve = getattr(child, "FCurve", None)
            digest = self._fcurve_digest(fcurve)
            if digest:
                parts.append("{0}:{1}".format(getattr(child, "Name", ""), digest))
        return "|".join(parts)

    def _scene_summary(self):
        scene = FBSystem().Scene
        take = FBSystem().CurrentTake
        component_types = {}
        model_count = 0
        user_camera_count = 0
        marker_count = 0
        character_count = 0
        constraint_names = []
        take_names = []
        layer_names = []
        parent_pairs = []
        transform_values = []
        transform_key_digests = []
        interesting_names = []
        for current_take in scene.Takes:
            try:
                take_names.append(str(current_take.Name))
            except Exception:
                pass
        if take is not None:
            try:
                for index in range(int(take.GetLayerCount())):
                    layer = take.GetLayer(index)
                    if layer is not None:
                        layer_names.append(str(layer.Name))
            except Exception:
                pass
        for component in scene.Components:
            type_name = type(component).__name__
            component_types[type_name] = component_types.get(type_name, 0) + 1
            long_name = _component_long_name(component)
            short_name = _short_name_from_long_name(long_name)
            if short_name:
                lowered = short_name.lower()
                if any(token in lowered for token in ("constraint", "marker", "camera", "character", "aminate", "history")):
                    interesting_names.append(short_name)
            if isinstance(component, FBCharacter):
                character_count += 1
            if isinstance(component, FBModel):
                model_count += 1
                if isinstance(component, FBCamera):
                    short_camera = short_name
                    if not short_camera.startswith("Producer "):
                        user_camera_count += 1
                if isinstance(component, (FBModelMarker, FBModelMarkerOptical)):
                    marker_count += 1
                try:
                    parent = component.Parent
                except Exception:
                    parent = None
                parent_pairs.append("{0}>{1}".format(short_name, _short_name_from_long_name(_component_long_name(parent))))
                for prop_name in TRANSFORM_PROPERTY_NAMES:
                    prop = component.PropertyList.Find(prop_name, False)
                    if prop is None:
                        continue
                    value = _vector_to_tuple(getattr(prop, "Data", None))
                    transform_values.append("{0}:{1}:{2}".format(short_name, prop_name, value))
                    digest = self._property_animation_digest(prop)
                    if digest:
                        transform_key_digests.append("{0}:{1}:{2}".format(short_name, prop_name, digest))
            if "Constraint" in type_name or short_name.lower().startswith("constraint"):
                constraint_names.append(short_name or long_name)
                try:
                    weight_prop = component.PropertyList.Find("Weight", False)
                except Exception:
                    weight_prop = None
                if weight_prop is not None:
                    digest = self._property_animation_digest(weight_prop)
                    if digest:
                        transform_key_digests.append("{0}:Weight:{1}".format(short_name, digest))
        transform_digest = _hash_payload(sorted(transform_values))
        key_digest = _hash_payload(sorted(transform_key_digests))
        parenting_digest = _hash_payload(sorted(parent_pairs))
        return {
            "current_time": self._player_frame(),
            "current_take": str(take.Name) if take is not None else "",
            "take_names": sorted(take_names),
            "take_digest": _hash_payload(sorted(take_names)),
            "animation_layers": layer_names,
            "animation_layer_digest": _hash_payload(sorted(layer_names)),
            "component_types": component_types,
            "model_count": model_count,
            "user_camera_count": user_camera_count,
            "marker_count": marker_count,
            "character_count": character_count,
            "constraint_names": sorted(constraint_names),
            "constraint_digest": _hash_payload(sorted(constraint_names)),
            "interesting_names": sorted(set(interesting_names))[:64],
            "transform_digest": transform_digest,
            "transform_values_count": len(transform_values),
            "key_digest": key_digest,
            "key_digest_count": len(transform_key_digests),
            "parenting_digest": parenting_digest,
        }

    def _scene_summary_changed(self, previous_summary, current_summary):
        previous_summary = previous_summary or {}
        current_summary = current_summary or {}
        keys = (
            "take_digest",
            "animation_layer_digest",
            "constraint_digest",
            "transform_digest",
            "key_digest",
            "parenting_digest",
            "component_types",
            "model_count",
            "user_camera_count",
            "marker_count",
            "character_count",
        )
        for key in keys:
            if previous_summary.get(key) != current_summary.get(key):
                return True
        return False

    def _is_timeline_scrub_action(self, previous_summary, current_summary):
        previous_summary = previous_summary or {}
        current_summary = current_summary or {}
        if not previous_summary or not current_summary:
            return False
        if previous_summary.get("current_time") == current_summary.get("current_time"):
            return False
        stable_keys = (
            "take_digest",
            "animation_layer_digest",
            "constraint_digest",
            "transform_digest",
            "key_digest",
            "parenting_digest",
            "component_types",
            "model_count",
            "user_camera_count",
            "marker_count",
            "character_count",
        )
        for key in stable_keys:
            if previous_summary.get(key) != current_summary.get(key):
                return False
        return True

    def _classify_auto_snapshot_action(self, previous_summary, current_summary):
        previous_summary = previous_summary or {}
        current_summary = current_summary or {}
        triggers = set()
        if previous_summary.get("key_digest") != current_summary.get("key_digest"):
            triggers.add("keyframes")
        if previous_summary.get("constraint_digest") != current_summary.get("constraint_digest"):
            triggers.add("constraints")
        if previous_summary.get("animation_layer_digest") != current_summary.get("animation_layer_digest"):
            triggers.add("animation_layers")
        if previous_summary.get("parenting_digest") != current_summary.get("parenting_digest"):
            triggers.add("parenting")
        if previous_summary.get("take_digest") != current_summary.get("take_digest"):
            triggers.add("takes")
        if previous_summary.get("transform_digest") != current_summary.get("transform_digest"):
            triggers.add("transforms")
        node_keys = ("component_types", "model_count", "user_camera_count", "marker_count", "character_count")
        for key in node_keys:
            if previous_summary.get(key) != current_summary.get(key):
                triggers.add("nodes")
                break
        return triggers or {"transforms"}

    def _auto_snapshot_settings_from_manifest(self, manifest):
        mode = manifest.get("auto_snapshot_mode") or DEFAULT_AUTO_SNAPSHOT_MODE
        if mode not in (AUTO_SNAPSHOT_MODE_ALL, AUTO_SNAPSHOT_MODE_CUSTOM):
            mode = DEFAULT_AUTO_SNAPSHOT_MODE
        stored = manifest.get("auto_snapshot_triggers") or {}
        triggers = dict(DEFAULT_AUTO_SNAPSHOT_TRIGGERS)
        for key in triggers:
            if key in stored:
                triggers[key] = bool(stored[key])
        return {"mode": mode, "triggers": triggers}

    def auto_snapshot_enabled(self):
        context = self._context()
        if not context.get("ok"):
            return DEFAULT_AUTO_SNAPSHOT_ENABLED
        manifest = self._load_manifest(context)
        return bool(manifest.get("auto_snapshot_enabled", DEFAULT_AUTO_SNAPSHOT_ENABLED))

    def set_auto_snapshot_enabled(self, enabled, parent=None):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not update Auto History.")
        manifest = self._load_manifest(context)
        manifest["auto_snapshot_enabled"] = bool(enabled)
        self._save_manifest(context, manifest)
        if enabled:
            self.start_default_action_snapshots(parent=parent)
            self._emit_status("Auto History is on.", True)
        else:
            self.stop_default_action_snapshots()
            self._emit_status("Auto History is off. Manual Save Step still works.", True)
        return True, "Auto History updated."

    def auto_snapshot_settings(self):
        context = self._context()
        if not context.get("ok"):
            return {"mode": DEFAULT_AUTO_SNAPSHOT_MODE, "triggers": dict(DEFAULT_AUTO_SNAPSHOT_TRIGGERS)}
        manifest = self._load_manifest(context)
        return self._auto_snapshot_settings_from_manifest(manifest)

    def set_auto_snapshot_settings(self, mode=DEFAULT_AUTO_SNAPSHOT_MODE, triggers=None):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not update Auto History rules.")
        manifest = self._load_manifest(context)
        current = self._auto_snapshot_settings_from_manifest(manifest)
        merged = dict(current["triggers"])
        for key in merged:
            if triggers and key in triggers:
                merged[key] = bool(triggers[key])
        manifest["auto_snapshot_mode"] = mode if mode in (AUTO_SNAPSHOT_MODE_ALL, AUTO_SNAPSHOT_MODE_CUSTOM) else DEFAULT_AUTO_SNAPSHOT_MODE
        manifest["auto_snapshot_triggers"] = merged
        manifest.setdefault("events", []).append({"type": "auto_snapshot_settings", "timestamp": _now_iso()})
        self._save_manifest(context, manifest)
        return True, "Auto History rules updated."

    def _mark_action_baseline(self, summary=None):
        self._pending_summary = None
        self._pending_action_time = 0.0
        self._last_action_summary = summary or self._scene_summary()

    def _mark_restore_baseline(self, summary=None, settle_seconds=6.0):
        self._restored_summary = summary or self._scene_summary()
        self._restore_settle_until = time.time() + float(settle_seconds or 0.0)
        self._mark_action_baseline(self._restored_summary)

    def _is_restore_settling(self, current_summary):
        if time.time() >= self._restore_settle_until:
            self._restored_summary = None
            self._restore_settle_until = 0.0
            return False
        if not self._scene_summary_changed(self._restored_summary, current_summary):
            return True
        return False

    def start_default_action_snapshots(self, parent=None):
        if QtCore is None:
            return False, "Auto History needs PySide."
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Open a writable scene first.")
        if self._action_timer is not None:
            return True, "Auto History already watching."
        self._mark_action_baseline()
        self._action_timer = QtCore.QTimer(parent)
        self._action_timer.setInterval(AUTO_SNAPSHOT_INTERVAL_MS)
        self._action_timer.timeout.connect(self._maybe_snapshot_after_action)
        self._action_timer.start()
        return True, "Auto History now watches scene changes."

    def stop_default_action_snapshots(self):
        timer = self._action_timer
        self._action_timer = None
        if timer is not None:
            try:
                timer.stop()
            except Exception:
                pass
            try:
                timer.deleteLater()
            except Exception:
                pass

    def _maybe_snapshot_after_action(self):
        if not self.auto_snapshot_enabled():
            self.stop_default_action_snapshots()
            return
        if self._auto_snapshot_busy:
            return
        context = self._context()
        if not context.get("ok"):
            return
        if self._auto_snapshots_are_suppressed():
            self._mark_action_baseline()
            return
        self._auto_snapshot_busy = True
        try:
            current_summary = self._scene_summary()
            if self._is_restore_settling(current_summary):
                self._mark_action_baseline(current_summary)
                return
            if self._is_timeline_scrub_action(self._last_action_summary, current_summary):
                self._mark_action_baseline(current_summary)
                return
            if not self._scene_summary_changed(self._last_action_summary, current_summary):
                self._mark_action_baseline(current_summary)
                return
            if self._pending_summary is None:
                self._pending_summary = current_summary
                self._pending_action_time = time.time()
                return
            if self._scene_summary_changed(self._pending_summary, current_summary):
                self._pending_summary = current_summary
                self._pending_action_time = time.time()
                return
            if time.time() - self._pending_action_time < AUTO_SNAPSHOT_SETTLE_SECONDS:
                return
            self.create_post_action_snapshot()
        finally:
            self._auto_snapshot_busy = False

    def create_post_action_snapshot(self):
        if not self.auto_snapshot_enabled():
            return False, "Auto History is off.", None
        previous_summary = self._last_action_summary or {}
        current_summary = self._pending_summary or self._scene_summary()
        manifest = self._load_manifest(self._context())
        settings = self._auto_snapshot_settings_from_manifest(manifest)
        action_types = self._classify_auto_snapshot_action(previous_summary, current_summary)
        if settings["mode"] == AUTO_SNAPSHOT_MODE_CUSTOM:
            matched = sorted(key for key in action_types if settings["triggers"].get(key, False))
            if not matched:
                self._mark_action_baseline(current_summary)
                return False, "Auto history skipped after unmatched change.", None
            reason = ", ".join(matched)
        else:
            reason = ", ".join(sorted(action_types))
        label = "Auto - {0}".format(reason.title())
        note = "Auto snapshot after MotionBuilder change types: {0}.".format(", ".join(sorted(action_types)))
        success, message, record = self.create_snapshot(label=label, color=DEFAULT_AUTO_COLOR, note=note, auto=True, reason=reason)
        return success, message, record

    def create_snapshot(self, label="", color="", milestone=False, note="", auto=False, reason=""):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not create snapshot."), None
        self._suppress_auto_snapshots_for(2.0)
        manifest = self._load_manifest(context)
        snapshot_id = "snap_{0}_{1}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), uuid.uuid4().hex[:8])
        label = (label or "").strip()
        if not label:
            if milestone:
                label = "Milestone"
            elif auto:
                label = "Auto - Safety"
            else:
                label = "Manual saved step"
        note = (note or "").strip()
        if not note and not auto:
            note = "Manual snapshot saved on frame {0} in take {1}.".format(self._player_frame(), FBSystem().CurrentTake.Name)
        frame_value = self._player_frame()
        parent_id = manifest.get("current_snapshot_id", "")
        active_branch = manifest.get("active_branch_id", "main") or "main"
        branched_from_id = ""
        branched_from_label = ""
        parent_record = self._snapshot_for_id(manifest, parent_id)
        parent_branch = (parent_record.get("branch_id") if parent_record else active_branch) or active_branch
        if parent_id and snapshots_has_future(manifest, parent_id, branch_id=parent_branch):
            active_branch = self._create_branch(manifest, parent_id)
            branched_from_id = parent_id
            branched_from_label = parent_record.get("label", parent_id) if parent_record else parent_id
        branch_info = self._branch_record(manifest, active_branch)
        branch_color = branch_info.get("color") or self._branch_color_from_id(active_branch)
        summary = self._scene_summary()
        record = {
            "id": snapshot_id,
            "label": label,
            "color": (color or "").strip() or (DEFAULT_MILESTONE_COLOR if milestone else branch_color),
            "note": note,
            "frame": frame_value,
            "take": str(FBSystem().CurrentTake.Name) if FBSystem().CurrentTake else "",
            "timestamp": _now_iso(),
            "milestone": bool(milestone),
            "locked": bool(milestone),
            "auto": bool(auto),
            "reason": reason or "",
            "parent_id": parent_id,
            "branch_id": active_branch,
            "branch_label": branch_info.get("label") or "Main",
            "branch_color": branch_color,
            "branched_from_id": branched_from_id,
            "branched_from_label": branched_from_label,
            "original_scene_path": context.get("original_scene_path", ""),
            "snapshot_path": "",
            "snapshot_size_bytes": 0,
            "scene_summary": summary,
        }
        snapshot_name = "{0}_{1}.fbx".format(snapshot_id, _safe_name(label))
        record["snapshot_path"] = os.path.join(context["snapshot_dir"], snapshot_name)
        if not os.path.isdir(context["snapshot_dir"]):
            os.makedirs(context["snapshot_dir"])
        success = bool(FBApplication().FileExport(record["snapshot_path"]))
        if not success or not os.path.exists(record["snapshot_path"]):
            return False, "Could not export MotionBuilder snapshot file.", None
        record["snapshot_size_bytes"] = _snapshot_file_size(record)
        manifest.setdefault("snapshots", []).append(record)
        manifest["current_snapshot_id"] = snapshot_id
        manifest["active_branch_id"] = active_branch
        manifest.setdefault("events", []).append(
            {"type": "create", "snapshot_id": snapshot_id, "timestamp": record["timestamp"], "reason": reason or ""}
        )
        self._apply_snapshot_cap(context, manifest)
        self._mark_action_baseline(summary)
        _notify_history_ui_changed()
        message = "Saved {0}: {1}".format("milestone" if milestone else ("auto snapshot" if auto else "step"), label)
        self._emit_status(message, True)
        return True, message, record

    def _apply_snapshot_cap(self, context, manifest):
        cap = int(manifest.get("snapshot_cap") or 0)
        snapshots = manifest.get("snapshots") or []
        if cap <= 0 or len(snapshots) <= cap:
            self._save_manifest(context, manifest)
            return
        keep_ids = set(record.get("id") for record in snapshots if record.get("milestone") or record.get("locked"))
        removable = [record for record in snapshots if record.get("id") not in keep_ids]
        removed_ids = []
        while len(snapshots) > cap and removable:
            victim = removable.pop(0)
            snapshot_path = victim.get("snapshot_path", "")
            if snapshot_path and os.path.exists(snapshot_path):
                try:
                    os.remove(snapshot_path)
                except Exception:
                    pass
            snapshots.remove(victim)
            removed_ids.append(victim.get("id"))
        if removed_ids:
            manifest.setdefault("events", []).append(
                {"type": "cap_cleanup", "timestamp": _now_iso(), "snapshot_ids": removed_ids}
            )
            current_id = manifest.get("current_snapshot_id", "")
            if current_id in removed_ids:
                manifest["current_snapshot_id"] = snapshots[-1]["id"] if snapshots else ""
        self._save_manifest(context, manifest)

    def restore_snapshot(self, snapshot_id, save_current_first=False):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not restore snapshot.")
        manifest = self._load_manifest(context)
        record = self._snapshot_for_id(manifest, snapshot_id)
        if not record:
            return False, "Pick a History snapshot to restore."
        if save_current_first:
            self.create_snapshot(label="Pre Restore Safety", color=DEFAULT_AUTO_COLOR, note="Automatic pre-restore safety snapshot.")
            context = self._context()
            manifest = self._load_manifest(context)
            record = self._snapshot_for_id(manifest, snapshot_id)
        snapshot_path = record.get("snapshot_path", "")
        if not snapshot_path or not os.path.exists(snapshot_path):
            return False, "Snapshot file is missing: {0}".format(snapshot_path)
        was_watching = self._action_timer is not None
        self.stop_default_action_snapshots()
        self._auto_snapshot_busy = True
        self._suppress_auto_snapshots_for(6.0)
        suspended_widgets = _suspend_history_widgets()
        runtime_shutdown = _shutdown_aminate_mobu_runtime_for_restore()
        closed_tools = _close_known_fb_tools_for_restore()
        try:
            if not bool(FBApplication().FileOpen(snapshot_path, False)):
                return False, "MotionBuilder could not open the snapshot."
            if not bool(FBApplication().FileSave(context["original_scene_path"])):
                return False, "MotionBuilder restored the snapshot but could not rebind the original scene path."
        finally:
            self._auto_snapshot_busy = False
            _resume_history_widgets(suspended_widgets)
        context = self._context()
        manifest = self._load_manifest(context)
        manifest["current_snapshot_id"] = snapshot_id
        manifest["active_branch_id"] = record.get("branch_id", manifest.get("active_branch_id", "main"))
        manifest.setdefault("events", []).append({"type": "restore", "snapshot_id": snapshot_id, "timestamp": _now_iso()})
        self._save_manifest(context, manifest)
        self._mark_restore_baseline(record.get("scene_summary") or self._scene_summary(), settle_seconds=6.0)
        _notify_history_ui_changed()
        if was_watching and self.auto_snapshot_enabled():
            self.start_default_action_snapshots()
        message = "Restored snapshot: {0}".format(record.get("label", snapshot_id))
        if closed_tools:
            message += " Closed tools before reload: {0}.".format(", ".join(closed_tools))
        if runtime_shutdown:
            message += " Aminate Mobu runtime watchers were reset."
        self._emit_status(message, True)
        return True, message

    def delete_snapshot(self, snapshot_id, force=False):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not delete snapshot.")
        manifest = self._load_manifest(context)
        record = self._snapshot_for_id(manifest, snapshot_id)
        if not record:
            return False, "Pick a History snapshot to delete."
        if record.get("locked") and not force:
            return False, "Milestone snapshots are locked. Unlock before delete."
        snapshot_path = record.get("snapshot_path", "")
        if snapshot_path and os.path.exists(snapshot_path):
            try:
                os.remove(snapshot_path)
            except Exception as exc:
                return False, "Could not delete snapshot file: {0}".format(exc)
        manifest["snapshots"] = [item for item in manifest.get("snapshots", []) if item.get("id") != snapshot_id]
        if manifest.get("current_snapshot_id") == snapshot_id:
            manifest["current_snapshot_id"] = manifest["snapshots"][-1]["id"] if manifest.get("snapshots") else ""
        manifest.setdefault("events", []).append({"type": "delete", "snapshot_id": snapshot_id, "timestamp": _now_iso()})
        self._save_manifest(context, manifest)
        self._mark_action_baseline()
        _notify_history_ui_changed()
        return True, "Deleted snapshot: {0}".format(record.get("label", snapshot_id))

    def delete_all_snapshots(self, force=False):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not delete snapshots.")
        manifest = self._load_manifest(context)
        snapshots = list(manifest.get("snapshots") or [])
        if not force and any(record.get("locked") for record in snapshots):
            return False, "Some milestone snapshots are locked. Confirm delete all first."
        removed = 0
        for record in snapshots:
            snapshot_path = record.get("snapshot_path", "")
            if snapshot_path and os.path.exists(snapshot_path):
                try:
                    os.remove(snapshot_path)
                    removed += 1
                except Exception:
                    pass
        manifest = self._default_manifest(context)
        manifest.setdefault("events", []).append({"type": "delete_all", "timestamp": _now_iso(), "count": removed})
        self._save_manifest(context, manifest)
        self._mark_action_baseline()
        _notify_history_ui_changed()
        return True, "Deleted all snapshots: {0}".format(removed)

    def _edit_snapshot(self, snapshot_id, changes, message):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not update snapshot.")
        manifest = self._load_manifest(context)
        record = self._snapshot_for_id(manifest, snapshot_id)
        if not record:
            return False, "Pick a History snapshot first."
        record.update(changes)
        self._save_manifest(context, manifest)
        _notify_history_ui_changed()
        return True, message

    def rename_snapshot(self, snapshot_id, label):
        return self._edit_snapshot(snapshot_id, {"label": (label or "").strip() or "Snapshot"}, "Renamed snapshot.")

    def color_snapshot(self, snapshot_id, color):
        return self._edit_snapshot(snapshot_id, {"color": (color or "").strip() or DEFAULT_STEP_COLOR}, "Changed color.")

    def update_note(self, snapshot_id, note):
        return self._edit_snapshot(snapshot_id, {"note": note or ""}, "Updated note.")

    def set_snapshot_milestone(self, snapshot_id, milestone=True):
        is_milestone = bool(milestone)
        return self._edit_snapshot(
            snapshot_id,
            {"milestone": is_milestone, "locked": is_milestone},
            "Marked as milestone." if is_milestone else "Removed milestone mark.",
        )

    def lock_snapshot(self, snapshot_id, locked=True):
        return self._edit_snapshot(snapshot_id, {"locked": bool(locked)}, "Updated lock state.")

    def list_snapshots(self, branch_id=None):
        context = self._context()
        if not context.get("ok"):
            return []
        manifest = self._load_manifest(context)
        records = list(manifest.get("snapshots") or [])
        if branch_id and branch_id not in ("", "__all__"):
            records = [record for record in records if record.get("branch_id") == branch_id]
        return records[-MAX_TABLE_ROWS:]

    def active_branch_id(self):
        context = self._context()
        if not context.get("ok"):
            return "main"
        manifest = self._load_manifest(context)
        return manifest.get("active_branch_id", "main") or "main"

    def set_active_branch(self, branch_id):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not switch branch.")
        manifest = self._load_manifest(context)
        self._branch_record(manifest, branch_id)
        manifest["active_branch_id"] = branch_id or "main"
        manifest.setdefault("events", []).append({"type": "branch_switch", "branch_id": branch_id, "timestamp": _now_iso()})
        self._save_manifest(context, manifest)
        _notify_history_ui_changed()
        return True, "Switched active branch."

    def rename_branch(self, branch_id, label):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not rename branch.")
        manifest = self._load_manifest(context)
        branch = self._branch_record(manifest, branch_id)
        branch["label"] = (label or "").strip() or branch.get("label") or "Branch"
        for record in manifest.get("snapshots") or []:
            if record.get("branch_id") == branch_id:
                record["branch_label"] = branch["label"]
        manifest.setdefault("events", []).append({"type": "branch_rename", "branch_id": branch_id, "timestamp": _now_iso()})
        self._save_manifest(context, manifest)
        _notify_history_ui_changed()
        return True, "Renamed branch."

    def branch_choices(self):
        context = self._context()
        if not context.get("ok"):
            return []
        manifest = self._load_manifest(context)
        self._ensure_branch_records(manifest)
        counts = {}
        for record in manifest.get("snapshots") or []:
            branch_id = record.get("branch_id") or "main"
            counts[branch_id] = counts.get(branch_id, 0) + 1
        output = []
        for branch_id, branch in sorted((manifest.get("branches") or {}).items(), key=lambda item: int(item[1].get("index") or 0)):
            output.append(
                {
                    "id": branch_id,
                    "label": branch.get("label", branch_id),
                    "count": counts.get(branch_id, 0),
                    "color": branch.get("color", self._branch_color_from_id(branch_id)),
                }
            )
        return output

    def restore_latest_in_branch(self, branch_id):
        snapshots = self.list_snapshots(branch_id=branch_id)
        if not snapshots:
            return False, "No snapshots in that branch."
        target = snapshots[-1]
        return self.restore_snapshot(target.get("id", ""), save_current_first=False)

    def snapshot_cap(self):
        context = self._context()
        if not context.get("ok"):
            return DEFAULT_SNAPSHOT_CAP
        manifest = self._load_manifest(context)
        return int(manifest.get("snapshot_cap") or DEFAULT_SNAPSHOT_CAP)

    def set_snapshot_cap(self, cap):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not update cap.")
        manifest = self._load_manifest(context)
        manifest["snapshot_cap"] = max(1, int(cap or DEFAULT_SNAPSHOT_CAP))
        self._apply_snapshot_cap(context, manifest)
        _notify_history_ui_changed()
        return True, "Snapshot cap updated."

    def history_storage_bytes(self):
        context = self._context()
        if not context.get("ok"):
            return 0
        manifest = self._load_manifest(context)
        return int(manifest.get("history_storage_size_bytes") or 0)

    def open_history_folder(self):
        context = self._context()
        if not context.get("ok"):
            return False, context.get("message", "Could not open history folder.")
        if not os.path.isdir(context["history_root"]):
            os.makedirs(context["history_root"])
        try:
            os.startfile(context["history_root"])
            return True, "Opened history folder."
        except Exception as exc:
            return False, "Could not open folder: {0}".format(exc)


if QtWidgets:
    class HistorySnapshotStrip(QtWidgets.QScrollArea):
        snapshotSelected = QtCore.Signal(str)
        restoreRequested = QtCore.Signal(str)

        def __init__(self, parent=None):
            super(HistorySnapshotStrip, self).__init__(parent)
            self.setObjectName("toolkitBarHistoryTimelineStrip")
            self.setWidgetResizable(True)
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setMinimumHeight(24)
            self.setMaximumHeight(28)
            if hasattr(self, "setSizePolicy"):
                self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            self._selected_id = ""
            self._inner = QtWidgets.QWidget()
            self._inner.setObjectName("toolkitBarHistoryTimelineStripInner")
            self._layout = QtWidgets.QHBoxLayout(self._inner)
            self._layout.setContentsMargins(4, 2, 4, 2)
            self._layout.setSpacing(2)
            self._layout.addStretch(1)
            self.setWidget(self._inner)
            self.setStyleSheet(
                """
                QScrollArea#toolkitBarHistoryTimelineStrip {
                    background-color: #191919;
                    border: 1px solid #363636;
                    border-radius: 4px;
                }
                QWidget#toolkitBarHistoryTimelineStripInner {
                    background: transparent;
                }
                """
            )

        def set_selected_snapshot_id(self, snapshot_id):
            self._selected_id = snapshot_id or ""

        def refresh(self, snapshots):
            while self._layout.count():
                item = self._layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            snapshots = list(snapshots or [])[-MAX_STRIP_MARKERS:]
            for record in snapshots:
                button = QtWidgets.QToolButton()
                button.setObjectName("toolkitBarHistoryMarker")
                color = record.get("color") or DEFAULT_STEP_COLOR
                border = "#FFFFFF" if record.get("id") == self._selected_id else "#2A2A2A"
                button.setText("")
                button.setMinimumSize(10, 12)
                button.setMaximumSize(12, 14)
                button.setStyleSheet(
                    "QToolButton#toolkitBarHistoryMarker { background-color:%s; border:2px solid %s; border-radius:2px; }"
                    "QToolButton#toolkitBarHistoryMarker:hover { border-color:#DCEEFF; }" % (color, border)
                )
                button.setToolTip(
                    "{0}\nBranch: {1}\nFrame: {2}\nTake: {3}\n{4}".format(
                        record.get("label", ""),
                        record.get("branch_label", ""),
                        record.get("frame", ""),
                        record.get("take", ""),
                        record.get("note", ""),
                    )
                )
                button.clicked.connect(lambda _checked=False, sid=record.get("id", ""): self.snapshotSelected.emit(sid))
                button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda _point, sid=record.get("id", ""): self.restoreRequested.emit(sid))
                self._layout.addWidget(button)
            self._layout.addStretch(1)


    class MotionBuilderHistoryTimelinePanel(QtWidgets.QWidget):
        def __init__(self, controller=None, parent=None):
            super(MotionBuilderHistoryTimelinePanel, self).__init__(parent)
            self.controller = controller or MotionBuilderHistoryTimelineController()
            self.controller.set_status_callback(self._set_status)
            self._selected_snapshot_id = ""
            self._refreshing_table = False
            self.setObjectName("AminateMobuHistoryTimelinePanel")
            _register_history_widget(self)
            self._build_ui()
            if self.controller.auto_snapshot_enabled():
                self.controller.start_default_action_snapshots(parent=self)
            self.refresh()

        def closeEvent(self, event):
            _unregister_history_widget(self)
            super(MotionBuilderHistoryTimelinePanel, self).closeEvent(event)

        def _build_ui(self):
            self.setStyleSheet(
                """
                QWidget#AminateMobuHistoryTimelinePanel {
                    background-color: #2B2B2B;
                    color: #E8E8E8;
                }
                QTableWidget {
                    background-color: #202020;
                    color: #EFEFEF;
                    gridline-color: #3C3C3C;
                    selection-background-color: #335C67;
                    border: 1px solid #3C3C3C;
                }
                QHeaderView::section {
                    background-color: #303030;
                    color: #F2F2F2;
                    border: 1px solid #3C3C3C;
                    padding: 4px 6px;
                    font-weight: 600;
                }
                QPushButton {
                    background-color: #3A3A3A;
                    color: #F2F2F2;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 5px 8px;
                }
                QPushButton:hover {
                    background-color: #454545;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #1E1E1E;
                    color: #F2F2F2;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 4px;
                }
                QCheckBox {
                    color: #E8E8E8;
                    spacing: 5px;
                }
                QLabel#AminateMobuHistoryStatus {
                    background-color: #202020;
                    color: #F2F2F2;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px 8px;
                }
                QLabel#AminateMobuHistoryStatus[state="neutral"] {
                    background-color: #202020;
                    color: #F2F2F2;
                    border-color: #444444;
                }
                QLabel#AminateMobuHistoryStatus[state="success"] {
                    background-color: #243326;
                    color: #C8F7D0;
                    border-color: #7BD88F;
                }
                QLabel#AminateMobuHistoryStatus[state="warning"] {
                    background-color: #3B2E1E;
                    color: #FFD88A;
                    border-color: #F6C85F;
                }
                QFrame#mayaAnimWorkflowTabIntro {
                    background-color: #353535;
                    color: #E8E8E8;
                    border: 1px solid #4A4A4A;
                    border-left: 4px solid #4CC9F0;
                    border-radius: 8px;
                }
                QLabel#mayaAnimWorkflowIntroTitle {
                    color: #F2F2F2;
                    font-weight: 700;
                }
                QLabel#AminateMobuHistoryIntroBody {
                    color: #C9C9C9;
                }
                """
            )
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(6)

            intro_frame = QtWidgets.QFrame()
            intro_frame.setObjectName("mayaAnimWorkflowTabIntro")
            intro_layout = QtWidgets.QVBoxLayout(intro_frame)
            intro_layout.setContentsMargins(10, 8, 10, 8)
            intro_layout.setSpacing(4)
            title = QtWidgets.QLabel("Aminate Mobu History Timeline")
            title.setObjectName("mayaAnimWorkflowIntroTitle")
            intro_layout.addWidget(title)
            intro = QtWidgets.QLabel(
                "Full-scene MotionBuilder history. Save steps, restore older states, branch safely, and let Auto History capture scene changes in the background."
            )
            intro.setWordWrap(True)
            intro.setObjectName("AminateMobuHistoryIntroBody")
            intro_layout.addWidget(intro)
            layout.addWidget(intro_frame)

            self.strip = HistorySnapshotStrip()
            self.strip.snapshotSelected.connect(self._select_snapshot_from_strip)
            self.strip.restoreRequested.connect(self._restore_from_marker)
            layout.addWidget(self.strip)

            branch_row = QtWidgets.QHBoxLayout()
            self.branch_combo = QtWidgets.QComboBox()
            self.branch_combo.currentIndexChanged.connect(self._branch_filter_changed)
            self.branch_name_field = QtWidgets.QLineEdit()
            self.branch_name_field.setPlaceholderText("Branch name")
            self.rename_branch_button = QtWidgets.QPushButton("Rename Branch")
            self.rename_branch_button.clicked.connect(self._rename_branch)
            self.switch_branch_button = QtWidgets.QPushButton("Switch To Branch")
            self.switch_branch_button.clicked.connect(self._switch_branch)
            branch_row.addWidget(QtWidgets.QLabel("Branch"))
            branch_row.addWidget(self.branch_combo, 1)
            branch_row.addWidget(self.branch_name_field, 1)
            branch_row.addWidget(self.rename_branch_button)
            branch_row.addWidget(self.switch_branch_button)
            layout.addLayout(branch_row)

            save_row = QtWidgets.QHBoxLayout()
            self.label_field = QtWidgets.QLineEdit()
            self.label_field.setPlaceholderText("Snapshot label")
            self.color_field = QtWidgets.QLineEdit(DEFAULT_STEP_COLOR)
            self.color_field.setMaximumWidth(110)
            self.note_field = QtWidgets.QLineEdit()
            self.note_field.setPlaceholderText("Snapshot note")
            save_row.addWidget(QtWidgets.QLabel("Label"))
            save_row.addWidget(self.label_field, 1)
            save_row.addWidget(QtWidgets.QLabel("Color"))
            save_row.addWidget(self.color_field)
            save_row.addWidget(QtWidgets.QLabel("Note"))
            save_row.addWidget(self.note_field, 2)
            layout.addLayout(save_row)

            action_row = QtWidgets.QHBoxLayout()
            self.save_button = QtWidgets.QPushButton("Save Step")
            self.save_button.clicked.connect(self._save_step)
            self.milestone_button = QtWidgets.QPushButton("Save Milestone")
            self.milestone_button.clicked.connect(self._save_milestone)
            self.restore_button = QtWidgets.QPushButton("Restore")
            self.restore_button.clicked.connect(self._restore)
            self.rename_button = QtWidgets.QPushButton("Rename")
            self.rename_button.clicked.connect(self._rename)
            self.color_button = QtWidgets.QPushButton("Apply Color")
            self.color_button.clicked.connect(self._color)
            self.toggle_milestone_button = QtWidgets.QPushButton("Mark Milestone")
            self.toggle_milestone_button.clicked.connect(self._toggle_milestone)
            self.delete_button = QtWidgets.QPushButton("Delete")
            self.delete_button.clicked.connect(self._delete)
            self.delete_all_button = QtWidgets.QPushButton("Delete All")
            self.delete_all_button.clicked.connect(self._delete_all)
            for widget in (
                self.save_button,
                self.milestone_button,
                self.restore_button,
                self.rename_button,
                self.color_button,
                self.toggle_milestone_button,
                self.delete_button,
                self.delete_all_button,
            ):
                action_row.addWidget(widget)
            layout.addLayout(action_row)

            auto_row = QtWidgets.QHBoxLayout()
            self.auto_enabled_checkbox = QtWidgets.QCheckBox("Auto History")
            self.auto_enabled_checkbox.toggled.connect(self._auto_enabled_toggled)
            self.auto_full_checkbox = QtWidgets.QCheckBox("All changes")
            self.auto_full_checkbox.toggled.connect(self._auto_full_toggled)
            auto_row.addWidget(self.auto_enabled_checkbox)
            auto_row.addWidget(self.auto_full_checkbox)
            self.auto_trigger_checkboxes = {}
            for trigger_id, trigger_label in AUTO_SNAPSHOT_TRIGGER_LABELS:
                checkbox = QtWidgets.QCheckBox(trigger_label)
                self.auto_trigger_checkboxes[trigger_id] = checkbox
                auto_row.addWidget(checkbox)
            self.apply_auto_rules_button = QtWidgets.QPushButton("Apply Auto Rules")
            self.apply_auto_rules_button.clicked.connect(self._apply_auto_snapshot_rules)
            auto_row.addWidget(self.apply_auto_rules_button)
            layout.addLayout(auto_row)

            info_row = QtWidgets.QHBoxLayout()
            self.snapshot_cap_spin = QtWidgets.QSpinBox()
            self.snapshot_cap_spin.setRange(1, 999)
            self.apply_cap_button = QtWidgets.QPushButton("Apply Cap")
            self.apply_cap_button.clicked.connect(self._apply_cap)
            self.open_folder_button = QtWidgets.QPushButton("Open Folder")
            self.open_folder_button.clicked.connect(self._open_folder)
            self.storage_label = QtWidgets.QLabel("Storage: 0 B")
            info_row.addWidget(QtWidgets.QLabel("Snapshot Cap"))
            info_row.addWidget(self.snapshot_cap_spin)
            info_row.addWidget(self.apply_cap_button)
            info_row.addWidget(self.open_folder_button)
            info_row.addWidget(self.storage_label, 1)
            layout.addLayout(info_row)

            self.table = QtWidgets.QTableWidget(0, 9)
            self.table.setHorizontalHeaderLabels(
                ["Current", "Branch", "Frame", "Type", "Label", "Take", "Note", "Timestamp", "Size"]
            )
            self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.table.itemSelectionChanged.connect(self._on_table_selection_changed)
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.verticalHeader().setVisible(False)
            self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            header = self.table.horizontalHeader()
            header.setSectionsMovable(False)
            header.setMinimumSectionSize(36)
            self.table.setColumnWidth(0, 64)
            self.table.setColumnWidth(1, 130)
            self.table.setColumnWidth(2, 88)
            self.table.setColumnWidth(3, 64)
            self.table.setColumnWidth(4, 180)
            self.table.setColumnWidth(5, 120)
            self.table.setColumnWidth(6, 260)
            self.table.setColumnWidth(7, 150)
            self.table.setColumnWidth(8, 82)
            layout.addWidget(self.table, 1)

            self.status_label = QtWidgets.QLabel("")
            self.status_label.setObjectName("AminateMobuHistoryStatus")
            self.status_label.setProperty("state", "neutral")
            self.status_label.setWordWrap(True)
            layout.addWidget(self.status_label)

        def selected_snapshot_id(self):
            return self._selected_snapshot_id

        def _record_for_id(self, snapshot_id):
            for record in self.controller.list_snapshots(branch_id=None):
                if record.get("id") == snapshot_id:
                    return record
            return None

        def _set_status(self, message, success=True):
            self.status_label.setProperty("state", "success" if success else "warning")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            self.status_label.setText(str(message))

        def _select_snapshot_row(self, snapshot_id):
            self._selected_snapshot_id = snapshot_id or ""
            self.strip.set_selected_snapshot_id(self._selected_snapshot_id)
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.data(QtCore.Qt.UserRole) == snapshot_id:
                    self.table.selectRow(row)
                    break

        def _refresh_branch_combo(self):
            current_data = self.branch_combo.currentData() if self.branch_combo.count() else "__all__"
            active_branch = self.controller.active_branch_id()
            self.branch_combo.blockSignals(True)
            try:
                self.branch_combo.clear()
                self.branch_combo.addItem("All Branches", "__all__")
                for branch in self.controller.branch_choices():
                    self.branch_combo.addItem(
                        "{0} ({1})".format(branch.get("label", branch.get("id")), branch.get("count", 0)),
                        branch.get("id"),
                    )
                target = current_data if current_data is not None else "__all__"
                for index in range(self.branch_combo.count()):
                    if self.branch_combo.itemData(index) == target:
                        self.branch_combo.setCurrentIndex(index)
                        break
                else:
                    for index in range(self.branch_combo.count()):
                        if self.branch_combo.itemData(index) == active_branch:
                            self.branch_combo.setCurrentIndex(index)
                            break
            finally:
                self.branch_combo.blockSignals(False)
            self._refresh_branch_name_field()

        def _refresh_branch_name_field(self):
            branch_id = self._selected_branch_filter()
            branch_label = ""
            if branch_id and branch_id != "__all__":
                for branch in self.controller.branch_choices():
                    if branch.get("id") == branch_id:
                        branch_label = branch.get("label", "")
                        break
            self.branch_name_field.setEnabled(bool(branch_id and branch_id != "__all__"))
            self.rename_branch_button.setEnabled(bool(branch_id and branch_id != "__all__"))
            self.switch_branch_button.setEnabled(bool(branch_id and branch_id != "__all__"))
            self.branch_name_field.setText(branch_label)

        def _selected_branch_filter(self):
            if self.branch_combo.currentIndex() < 0:
                return "__all__"
            return self.branch_combo.currentData()

        def _branch_filter_changed(self, *_args):
            self._refresh_branch_name_field()
            self.refresh()

        def _switch_branch(self):
            branch_id = self._selected_branch_filter()
            if not branch_id or branch_id == "__all__":
                self._set_status("Pick a single branch before switching.", False)
                return
            success, message = self.controller.restore_latest_in_branch(branch_id)
            self._set_status(message, success)
            self.refresh()

        def _rename_branch(self):
            branch_id = self._selected_branch_filter()
            if not branch_id or branch_id == "__all__":
                self._set_status("Pick a single branch before renaming.", False)
                return
            success, message = self.controller.rename_branch(branch_id, self.branch_name_field.text())
            self._set_status(message, success)
            self.refresh()

        def _save_step(self):
            success, message, record = self.controller.create_snapshot(
                label=self.label_field.text(),
                color=self.color_field.text(),
                note=self.note_field.text(),
            )
            if success and record:
                self._selected_snapshot_id = record.get("id", "")
            self._set_status(message, success)
            self.refresh()

        def _save_milestone(self):
            success, message, record = self.controller.create_snapshot(
                label=self.label_field.text() or "Milestone",
                color=self.color_field.text() or DEFAULT_MILESTONE_COLOR,
                milestone=True,
                note=self.note_field.text(),
            )
            if success and record:
                self._selected_snapshot_id = record.get("id", "")
            self._set_status(message, success)
            self.refresh()

        def _restore_from_marker(self, snapshot_id):
            if snapshot_id:
                self._selected_snapshot_id = snapshot_id
            success, message = self.controller.restore_snapshot(snapshot_id, save_current_first=False)
            self._set_status(message, success)
            self.refresh()

        def _restore(self):
            snapshot_id = self.selected_snapshot_id()
            if not snapshot_id:
                self._set_status("Pick a snapshot first.", False)
                return
            answer = QtWidgets.QMessageBox.question(
                self,
                "Restore History Snapshot",
                "Restore the whole MotionBuilder scene to this snapshot and rebind the original working file?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if answer != QtWidgets.QMessageBox.Yes:
                return
            success, message = self.controller.restore_snapshot(snapshot_id, save_current_first=True)
            self._set_status(message, success)
            self.refresh()

        def _rename(self):
            snapshot_id = self.selected_snapshot_id()
            if not snapshot_id:
                self._set_status("Pick a snapshot first.", False)
                return
            record = self._record_for_id(snapshot_id) or {}
            new_label, accepted = QtWidgets.QInputDialog.getText(
                self,
                "Rename Snapshot",
                "New label",
                QtWidgets.QLineEdit.Normal,
                record.get("label", "Snapshot"),
            )
            if not accepted:
                return
            success, message = self.controller.rename_snapshot(snapshot_id, new_label)
            self._set_status(message, success)
            self.refresh()

        def _color(self):
            snapshot_id = self.selected_snapshot_id()
            if not snapshot_id:
                self._set_status("Pick a snapshot first.", False)
                return
            success, message = self.controller.color_snapshot(snapshot_id, self.color_field.text())
            self._set_status(message, success)
            self.refresh()

        def _toggle_milestone(self):
            snapshot_id = self.selected_snapshot_id()
            if not snapshot_id:
                self._set_status("Pick a snapshot first.", False)
                return
            record = self._record_for_id(snapshot_id) or {}
            success, message = self.controller.set_snapshot_milestone(snapshot_id, not bool(record.get("milestone")))
            self._set_status(message, success)
            self.refresh()

        def _delete(self):
            snapshot_id = self.selected_snapshot_id()
            if not snapshot_id:
                self._set_status("Pick a snapshot first.", False)
                return
            answer = QtWidgets.QMessageBox.question(
                self,
                "Delete Snapshot",
                "Delete this snapshot file and remove it from History Timeline?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if answer != QtWidgets.QMessageBox.Yes:
                return
            success, message = self.controller.delete_snapshot(snapshot_id)
            self._set_status(message, success)
            self.refresh()

        def _delete_all(self):
            answer = QtWidgets.QMessageBox.question(
                self,
                "Delete All Snapshots",
                "Delete every History Timeline snapshot for this MotionBuilder scene?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if answer != QtWidgets.QMessageBox.Yes:
                return
            success, message = self.controller.delete_all_snapshots(force=True)
            self._set_status(message, success)
            self.refresh()

        def _auto_enabled_toggled(self, checked):
            success, message = self.controller.set_auto_snapshot_enabled(bool(checked), parent=self)
            self._set_status(message, success)
            self._refresh_auto_snapshot_controls()

        def _auto_full_toggled(self, checked):
            for checkbox in self.auto_trigger_checkboxes.values():
                checkbox.setEnabled(self.controller.auto_snapshot_enabled() and not checked)

        def _apply_auto_snapshot_rules(self):
            mode = AUTO_SNAPSHOT_MODE_ALL if self.auto_full_checkbox.isChecked() else AUTO_SNAPSHOT_MODE_CUSTOM
            triggers = {key: checkbox.isChecked() for key, checkbox in self.auto_trigger_checkboxes.items()}
            success, message = self.controller.set_auto_snapshot_settings(mode=mode, triggers=triggers)
            self._set_status(message, success)
            self.refresh()

        def _apply_cap(self):
            success, message = self.controller.set_snapshot_cap(self.snapshot_cap_spin.value())
            self._set_status(message, success)
            self.refresh()

        def _open_folder(self):
            success, message = self.controller.open_history_folder()
            self._set_status(message, success)

        def _select_snapshot_from_strip(self, snapshot_id):
            self._select_snapshot_row(snapshot_id)
            self._fill_fields_from_selection()

        def _on_table_selection_changed(self):
            if self._refreshing_table:
                return
            items = self.table.selectedItems()
            if not items:
                self._selected_snapshot_id = ""
                return
            self._selected_snapshot_id = items[0].data(QtCore.Qt.UserRole) or ""
            self.strip.set_selected_snapshot_id(self._selected_snapshot_id)
            self._fill_fields_from_selection()

        def _fill_fields_from_selection(self):
            record = self._record_for_id(self._selected_snapshot_id) or {}
            if not record:
                return
            self.label_field.setText(record.get("label", ""))
            self.color_field.setText(record.get("color", DEFAULT_STEP_COLOR))
            self.note_field.setText(record.get("note", ""))
            self.toggle_milestone_button.setText("Clear Milestone" if record.get("milestone") else "Mark Milestone")

        def _refresh_auto_snapshot_controls(self):
            settings = self.controller.auto_snapshot_settings()
            enabled = self.controller.auto_snapshot_enabled()
            is_full = settings.get("mode") == AUTO_SNAPSHOT_MODE_ALL
            self.auto_enabled_checkbox.blockSignals(True)
            self.auto_enabled_checkbox.setChecked(bool(enabled))
            self.auto_enabled_checkbox.blockSignals(False)
            self.auto_full_checkbox.blockSignals(True)
            self.auto_full_checkbox.setChecked(is_full)
            self.auto_full_checkbox.setEnabled(bool(enabled))
            self.auto_full_checkbox.blockSignals(False)
            triggers = settings.get("triggers") or {}
            for key, checkbox in self.auto_trigger_checkboxes.items():
                checkbox.blockSignals(True)
                checkbox.setChecked(bool(triggers.get(key, DEFAULT_AUTO_SNAPSHOT_TRIGGERS.get(key, True))))
                checkbox.setEnabled(bool(enabled) and not is_full)
                checkbox.blockSignals(False)
            self.apply_auto_rules_button.setEnabled(bool(enabled))

        def refresh(self):
            context = self.controller._context()
            self._refresh_branch_combo()
            self._refresh_auto_snapshot_controls()
            self.snapshot_cap_spin.setValue(self.controller.snapshot_cap())
            self.storage_label.setText("Storage: {0}".format(_format_bytes(self.controller.history_storage_bytes())))
            branch_filter = self._selected_branch_filter()
            filter_branch_id = None if branch_filter in (None, "__all__") else branch_filter
            snapshots = self.controller.list_snapshots(branch_id=filter_branch_id)
            current_id = ""
            if context.get("ok"):
                manifest = self.controller._load_manifest(context)
                current_id = manifest.get("current_snapshot_id", "")
            previous_selected_id = self._selected_snapshot_id
            self._refreshing_table = True
            self.table.setRowCount(len(snapshots))
            for row, record in enumerate(snapshots):
                type_label = "Milestone" if record.get("milestone") else ("Auto" if record.get("auto") else "Step")
                values = [
                    "*" if record.get("id") == current_id else "",
                    record.get("branch_label", ""),
                    str(record.get("frame", "")),
                    type_label,
                    record.get("label", ""),
                    record.get("take", ""),
                    record.get("note", ""),
                    record.get("timestamp", ""),
                    _format_bytes(record.get("snapshot_size_bytes", 0)),
                ]
                for column, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(value)
                    item.setData(QtCore.Qt.UserRole, record.get("id", ""))
                    color = record.get("color") or DEFAULT_STEP_COLOR
                    if column in (0, 4):
                        item.setBackground(QtGui.QColor(color))
                        item.setForeground(QtGui.QColor("#081018"))
                    else:
                        item.setBackground(QtGui.QColor(32, 32, 32))
                        item.setForeground(QtGui.QColor("#EFEFEF"))
                    self.table.setItem(row, column, item)
            self._refreshing_table = False
            visible_ids = [record.get("id") for record in snapshots]
            target_id = previous_selected_id if previous_selected_id in visible_ids else (current_id if current_id in visible_ids else "")
            if target_id:
                self._select_snapshot_row(target_id)
            elif snapshots:
                self._select_snapshot_row(snapshots[-1].get("id", ""))
            else:
                self._selected_snapshot_id = ""
            self.strip.set_selected_snapshot_id(self._selected_snapshot_id)
            self.strip.refresh(snapshots)
            if not context.get("ok"):
                self._set_status(context.get("message", "Open a writable scene first."), False)


    class MotionBuilderHistoryTimelineWindow(QtWidgets.QDialog):
        def __init__(self, controller=None, parent=None):
            super(MotionBuilderHistoryTimelineWindow, self).__init__(parent or _qt_main_window())
            self.controller = controller or MotionBuilderHistoryTimelineController()
            self.setObjectName(WINDOW_OBJECT_NAME)
            self.setWindowTitle("Aminate Mobu History Timeline")
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.setMinimumSize(920, 560)
            self.resize(1500, 820)
            layout = QtWidgets.QVBoxLayout(self)
            self.panel = MotionBuilderHistoryTimelinePanel(self.controller, parent=self)
            layout.addWidget(self.panel)

        def closeEvent(self, event):
            global GLOBAL_CONTROLLER
            global GLOBAL_WINDOW
            try:
                self.panel.controller.shutdown()
            except Exception:
                pass
            GLOBAL_CONTROLLER = None
            GLOBAL_WINDOW = None
            super(MotionBuilderHistoryTimelineWindow, self).closeEvent(event)


def launch_motionbuilder_history_timeline():
    global GLOBAL_CONTROLLER
    global GLOBAL_WINDOW
    if QtWidgets is None:
        raise RuntimeError("Aminate Mobu History Timeline needs PySide.")
    if GLOBAL_WINDOW is not None:
        try:
            GLOBAL_WINDOW.show()
            GLOBAL_WINDOW.raise_()
            GLOBAL_WINDOW.activateWindow()
            GLOBAL_WINDOW.panel.refresh()
            return GLOBAL_WINDOW
        except Exception:
            GLOBAL_WINDOW = None
    GLOBAL_CONTROLLER = MotionBuilderHistoryTimelineController()
    GLOBAL_WINDOW = MotionBuilderHistoryTimelineWindow(GLOBAL_CONTROLLER)
    GLOBAL_WINDOW.show()
    return GLOBAL_WINDOW


__all__ = [
    "AMINATE_MOBU_HISTORY_VERSION",
    "DEFAULT_AUTO_SNAPSHOT_TRIGGERS",
    "DEFAULT_MILESTONE_COLOR",
    "DEFAULT_STEP_COLOR",
    "MANIFEST_FILE_NAME",
    "MotionBuilderHistoryTimelineController",
    "MotionBuilderHistoryTimelinePanel",
    "MotionBuilderHistoryTimelineWindow",
    "SNAPSHOT_FOLDER_NAME",
    "launch_motionbuilder_history_timeline",
    "snapshots_has_future",
]
