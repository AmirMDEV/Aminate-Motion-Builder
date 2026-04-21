"""
Aminate Mobu

MotionBuilder sibling toolkit for Aminate.
"""

from __future__ import annotations

import os
import re
import time
from collections import OrderedDict

from pyfbsdk import (
    FBAddRegionParam,
    FBApplication,
    FBBodyNodeId,
    FBButton,
    FBCharacter,
    FBCharacterKeyingMode,
    FBColor,
    FBAttachType,
    FBButtonLook,
    FBButtonState,
    FBButtonStyle,
    FBEdit,
    FBFindModelByLabelName,
    FBGetSelectedModels,
    FBLabel,
    FBMemo,
    FBMessageBox,
    FBModel,
    FBModelList,
    FBModelMarker,
    FBModelMarkerOptical,
    FBModelSkeleton,
    FBPopup,
    ShowTool,
    FBStringList,
    FBSystem,
    FBTextJustify,
    FBToolPossibleDockPosition,
)
import pyfbsdk_additions

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import getCppPointer, wrapInstance
except Exception:  # pragma: no cover - MotionBuilder fallback
    try:  # pragma: no cover - older MotionBuilder fallback
        from PySide2 import QtCore, QtGui, QtWidgets
        from shiboken2 import getCppPointer, wrapInstance
    except Exception:  # pragma: no cover - no Qt bridge available
        QtCore = None
        QtGui = None
        QtWidgets = None
        getCppPointer = None
        wrapInstance = None


TOOL_NAME = "Aminate Mobu"
TOOL_VERSION = "Version 0.1 BETA"
TOOL_DOC_TAG = "aminate_mobu_tool"
QT_WINDOW_OBJECT_NAME = "aminateMobuWindow"
QT_DOCK_OBJECT_NAME = "aminateMobuDock"
QT_LAUNCHER_TOOLBAR_OBJECT_NAME = "aminateMobuLauncherToolbar"
QT_LAUNCHER_BUTTON_OBJECT_NAME = "aminateMobuLauncherButton"
STARTUP_BOOTSTRAP_FILENAME = "aminate_mobu_startup.py"
MB_DOCUMENTS_ROOT = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "MB",
)
FOLLOW_AMIR_URL = "https://followamir.com"
DEFAULT_DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=2U2GXSKFJKJCA"
DONATE_URL = os.environ.get("AMIR_PAYPAL_DONATE_URL") or os.environ.get("AMIR_DONATE_URL") or DEFAULT_DONATE_URL
THEME_MOTIONBUILDER = "motionbuilder"
THEME_MODERN = "modern"
THEME_LABELS = OrderedDict(
    [
        (THEME_MOTIONBUILDER, "MotionBuilder"),
        (THEME_MODERN, "Modern"),
    ]
)
DEFAULT_THEME_KEY = THEME_MOTIONBUILDER
SCENE_CLEANER_HINT = (
    "Marker label is not exposed by MotionBuilder Python. "
    "Animated default markers are treated as prop markers, renamed with your chosen base name, and only non-animated junk markers are deleted."
)
LOCK_DEFINITION_WARNING = (
    "Your character map looks finished. Lock the character definition so MotionBuilder can use it properly."
)
CONTROL_RIG_MODE_WARNING = (
    "You need to be in a control rig body part or full body editing mode."
)
LOCK_WARNING_THROTTLE_SECONDS = 8.0
MODE_WARNING_THROTTLE_SECONDS = 2.0
DEFAULT_TOAST_DURATION_MS = 4000
DEFAULT_PROP_MARKER_BASE_NAME = "Prop"
UNLABELLED_MARKER_PATTERN = re.compile(r"^(marker|tmpmarker|unnamedmarker)(?:\s+\d+)?$", re.IGNORECASE)
CONTROL_RIG_PROPERTY_NAMES = {"Lcl Translation", "Lcl Rotation"}
AMINATE_MOBU_LOCAL_STYLESHEETS = {
THEME_MOTIONBUILDER: """
QWidget#aminateMobuWindow {
    background-color: #3A3A3A;
    color: #E2E2E2;
}
QLabel#aminateMobuHeaderTitle {
    color: #F0F0F0;
    font-size: 16px;
    font-weight: 700;
}
QLabel#aminateMobuHeaderSubtitle {
    color: #BDBDBD;
}
QLabel#aminateMobuThemeBadge {
    background-color: #2C2C2C;
    color: #D9D9D9;
    border: 1px solid #595959;
    border-radius: 3px;
    padding: 5px 10px;
}
QFrame#mayaAnimWorkflowTabIntro {
    background-color: #414141;
    color: #E8E8E8;
    border: 1px solid #5A5A5A;
    border-left: 3px solid #7C98AA;
    border-radius: 4px;
}
QLabel#mayaAnimWorkflowIntroTitle {
    color: #F2F2F2;
    font-weight: 700;
}
QLabel#mayaAnimWorkflowStatusLabel {
    background-color: #202020;
    color: #E8E8E8;
    border: 1px solid #3C3C3C;
    border-radius: 6px;
    padding: 6px 8px;
}
QLabel#mayaAnimWorkflowBrandLabel,
QLabel#mayaAnimWorkflowVersionLabel,
QLabel#aminateMobuGroupHint {
    color: #BDBDBD;
}
QPushButton#aminateMobuThemeToggle {
    background-color: #4D4D4D;
    border: 1px solid #707070;
    border-radius: 3px;
    padding: 5px 12px;
}
QPushButton#aminateMobuThemeToggle:hover {
    background-color: #565656;
}
QPushButton#aminateMobuThemeToggle:pressed {
    background-color: #616161;
    border-color: #8BA9BC;
}
QPushButton,
QToolButton {
    background-color: #4A4A4A;
    color: #F2F2F2;
    border: 1px solid #686868;
    border-radius: 3px;
    padding: 5px 8px;
}
QPushButton:hover,
QToolButton:hover {
    background-color: #555555;
    border-color: #7A7A7A;
}
QPushButton:pressed,
QToolButton:pressed {
    background-color: #606060;
    border-color: #8BA9BC;
}
QPushButton:disabled,
QToolButton:disabled {
    background-color: #262626;
    color: #777777;
    border-color: #363636;
}
QLineEdit,
QPlainTextEdit,
QTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: #262626;
    color: #F2F2F2;
    border: 1px solid #595959;
    border-radius: 3px;
    padding: 4px;
    selection-background-color: #506472;
}
QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-color: #8BA9BC;
}
QCheckBox,
QRadioButton,
QLabel {
    color: #E8E8E8;
}
QGroupBox {
    background-color: #3F3F3F;
    color: #F2F2F2;
    border: 1px solid #575757;
    border-radius: 4px;
    margin-top: 14px;
    padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 4px;
    color: #F2F2F2;
}
QScrollBar:vertical,
QScrollBar:horizontal {
    background-color: #202020;
    border: 0px;
    margin: 0px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background-color: #4A4A4A;
    border-radius: 4px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background-color: #5A5A5A;
}
QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
""",
THEME_MODERN: """
QWidget#aminateMobuWindow {
    background-color: #303234;
    color: #E4E7E9;
}
QLabel#aminateMobuHeaderTitle {
    color: #F0F2F3;
    font-size: 17px;
    font-weight: 700;
}
QLabel#aminateMobuHeaderSubtitle {
    color: #ACB4BB;
}
QLabel#aminateMobuThemeBadge {
    background-color: #3B3F43;
    color: #D7E0E7;
    border: 1px solid #555D64;
    border-radius: 10px;
    padding: 6px 12px;
}
QFrame#mayaAnimWorkflowTabIntro {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3A3D41, stop:1 #35383B);
    color: #E4E8EB;
    border: 1px solid #50565C;
    border-left: 4px solid #6B8192;
    border-radius: 12px;
}
QLabel#mayaAnimWorkflowIntroTitle {
    color: #F0F2F3;
    font-weight: 700;
}
QLabel#mayaAnimWorkflowStatusLabel {
    background-color: #26282A;
    color: #E3E7EA;
    border: 1px solid #444A50;
    border-radius: 10px;
    padding: 7px 10px;
}
QPlainTextEdit#aminateMobuStatusMemo {
    background-color: #242628;
    color: #E4E7E9;
    border: 1px solid #43484E;
    border-radius: 12px;
    padding: 6px;
}
QLabel#mayaAnimWorkflowBrandLabel,
QLabel#mayaAnimWorkflowVersionLabel,
QLabel#aminateMobuGroupHint {
    color: #A4ADB5;
}
QPushButton#aminateMobuThemeToggle {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #44494E, stop:1 #3E4348);
    border: 1px solid #646D75;
    border-radius: 10px;
    padding: 6px 14px;
    color: #EEF2F4;
}
QPushButton#aminateMobuThemeToggle:hover {
    background-color: #4D5359;
    border-color: #74808A;
}
QPushButton#aminateMobuThemeToggle:pressed {
    background-color: #585E65;
    border-color: #849AA9;
}
QPushButton,
QToolButton {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #545960, stop:1 #464A4F);
    color: #EEF1F3;
    border: 1px solid #747C84;
    border-radius: 9px;
    padding: 6px 10px;
}
QPushButton:hover,
QToolButton:hover {
    background-color: #5A6067;
    border-color: #89949D;
}
QPushButton:pressed,
QToolButton:pressed {
    background-color: #676D75;
    border-color: #9BAFBC;
}
QPushButton:checked,
QToolButton:checked {
    background-color: #606971;
    border-color: #9EB2BF;
}
QPushButton:disabled,
QToolButton:disabled {
    background-color: #252729;
    color: #737B82;
    border-color: #3A3F44;
}
QLineEdit,
QPlainTextEdit,
QTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: #2B2E31;
    color: #E4E7E9;
    border: 1px solid #555C63;
    border-radius: 9px;
    padding: 5px;
    selection-background-color: #50606D;
}
QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-color: #6B8090;
}
QCheckBox,
QRadioButton,
QLabel {
    color: #E2E6E9;
}
QGroupBox {
    background-color: #373A3D;
    color: #E7EAEC;
    border: 1px solid #50565B;
    border-radius: 12px;
    margin-top: 14px;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0px 5px;
    color: #E7EAEC;
}
QTabWidget::pane {
    border: 1px solid #545C63;
    border-radius: 11px;
    top: -1px;
    background-color: #323538;
}
QTabBar::tab {
    background-color: #3C4044;
    color: #DCE1E5;
    border: 1px solid #5E666E;
    border-bottom: 0px;
    border-top-left-radius: 9px;
    border-top-right-radius: 9px;
    padding: 7px 12px;
    margin-right: 2px;
}
QTabBar::tab:hover {
    background-color: #495057;
    color: #EEF2F4;
}
QTabBar::tab:selected {
    background-color: #5A626A;
    color: #F5F7F8;
    border-color: #8796A1;
}
QTabBar::tab:!selected {
    margin-top: 3px;
}
QScrollBar:vertical,
QScrollBar:horizontal {
    background-color: #26282A;
    border: 0px;
    margin: 0px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background-color: #5B6166;
    border-radius: 5px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background-color: #6A7177;
}
QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
""",
}
APP_THEME_STYLESHEETS = {
THEME_MOTIONBUILDER: "",
THEME_MODERN: """
QWidget {
    color: #E0E4E7;
    background-color: #454545;
    selection-background-color: #556674;
    selection-color: #F0F2F4;
}
QMainWindow,
QDialog,
QDockWidget,
QTabWidget::pane,
QStackedWidget,
QStatusBar,
QToolBar,
QMenuBar,
QMenu,
QAbstractScrollArea,
QTreeView,
QListView,
QTableView {
    background-color: #454545;
}
QMenuBar {
    border-bottom: 1px solid #5A5A5A;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    margin: 2px 2px;
    color: #E3E6E8;
}
QMenuBar::item:selected,
QMenu::item:selected {
    background-color: #5A6167;
    color: #F1F3F4;
}
QMenu {
    background-color: #3D3F42;
    border: 1px solid #5A5F64;
}
QMenu::item {
    padding: 6px 24px;
}
QToolBar {
    border: 0px;
    spacing: 4px;
}
QPushButton,
QToolButton,
QComboBox,
QAbstractSpinBox,
QLineEdit,
QPlainTextEdit,
QTextEdit {
    background-color: #4A4E53;
    color: #E7EAEC;
    border: 1px solid #707882;
    border-radius: 6px;
    padding: 4px 8px;
}
QPushButton:hover,
QToolButton:hover,
QComboBox:hover,
QAbstractSpinBox:hover {
    background-color: #5C636A;
    border-color: #8C98A2;
}
QPushButton:pressed,
QToolButton:pressed {
    background-color: #6A727A;
    border-color: #A0B4C1;
}
QPushButton:checked,
QToolButton:checked,
QToolButton:selected {
    background-color: #667079;
    border-color: #A3B7C4;
}
QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QAbstractSpinBox:focus {
    border: 1px solid #6D8293;
}
QHeaderView::section {
    background-color: #484B4F;
    color: #E3E7E9;
    border: 1px solid #61686E;
    padding: 4px 10px;
}
QTabWidget::pane {
    border: 1px solid #667079;
    top: -1px;
    background-color: #404346;
}
QTabBar::tab {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #50555A, stop:1 #464A4F);
    color: #E7EAEC;
    border: 1px solid #6E767E;
    border-bottom: 0px;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 5px 11px;
    margin-right: 2px;
}
QTabBar::tab:hover {
    background-color: #5A6066;
    color: #F4F6F7;
    border-color: #8A959F;
}
QTabBar::tab:selected {
    background-color: #667079;
    color: #F7F8F9;
    border-color: #A3B4C0;
}
QTabBar::tab:!selected {
    margin-top: 3px;
}
QTreeView,
QListView,
QTableView {
    alternate-background-color: #4B4E52;
    gridline-color: #5B6065;
    border: 1px solid #61676C;
}
QScrollBar:vertical,
QScrollBar:horizontal {
    background: #2A2C2E;
    border: 0px;
    margin: 0px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #5B6166;
    border-radius: 5px;
    min-height: 22px;
    min-width: 22px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background: #6C7379;
}
QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
QStatusBar {
    border-top: 1px solid #5A5A5A;
}
QGroupBox {
    border: 1px solid #5E6469;
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
    background-color: #404346;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 4px;
}
""",
}

CORE_REQUIRED_LINKS = (
    "HipsLink",
    "LeftUpLegLink",
    "LeftLegLink",
    "LeftFootLink",
    "RightUpLegLink",
    "RightLegLink",
    "RightFootLink",
    "SpineLink",
    "LeftArmLink",
    "LeftForeArmLink",
    "LeftHandLink",
    "RightArmLink",
    "RightForeArmLink",
    "RightHandLink",
    "HeadLink",
)

CHARACTER_SLOT_CANDIDATES = OrderedDict(
    [
        ("ReferenceLink", ("reference", "root")),
        ("HipsLink", ("hips", "pelvis")),
        ("HipsTranslationLink", ("hips", "pelvis")),
        ("LeftUpLegLink", ("leftupleg", "leftthigh", "lthigh")),
        ("LeftLegLink", ("leftleg", "leftcalf", "lcalf")),
        ("LeftFootLink", ("leftfoot", "lfoot")),
        ("LeftToeBaseLink", ("lefttoebase", "lefttoe", "ltoe")),
        ("RightUpLegLink", ("rightupleg", "rightthigh", "rthigh")),
        ("RightLegLink", ("rightleg", "rightcalf", "rcalf")),
        ("RightFootLink", ("rightfoot", "rfoot")),
        ("RightToeBaseLink", ("righttoebase", "righttoe", "rtoe")),
        ("SpineLink", ("spine", "waist")),
        ("Spine1Link", ("spine1", "spine01", "chest")),
        ("Spine2Link", ("spine2", "spine02", "upperchest")),
        ("Spine3Link", ("spine3",)),
        ("Spine4Link", ("spine4",)),
        ("Spine5Link", ("spine5",)),
        ("Spine6Link", ("spine6",)),
        ("Spine7Link", ("spine7",)),
        ("Spine8Link", ("spine8",)),
        ("Spine9Link", ("spine9",)),
        ("NeckLink", ("neck",)),
        ("Neck1Link", ("neck1", "neck01")),
        ("Neck2Link", ("neck2", "neck02")),
        ("HeadLink", ("head",)),
        ("LeftShoulderLink", ("leftshoulder", "leftclavicle", "lclavicle")),
        ("LeftArmLink", ("leftarm", "leftupperarm", "lupperarm")),
        ("LeftArmRollLink", ("leftarmroll", "leftuparmtwist", "luparmtwist")),
        ("LeftForeArmLink", ("leftforearm", "leftlowerarm", "lforearm", "llowerarm")),
        ("LeftForeArmRollLink", ("leftforearmroll", "leftforearmtwist", "lforearmtwist")),
        ("LeftHandLink", ("lefthand", "lwrist")),
        ("RightShoulderLink", ("rightshoulder", "rightclavicle", "rclavicle")),
        ("RightArmLink", ("rightarm", "rightupperarm", "rupperarm")),
        ("RightArmRollLink", ("rightarmroll", "rightuparmtwist", "ruparmtwist")),
        ("RightForeArmLink", ("rightforearm", "rightlowerarm", "rforearm", "rlowerarm")),
        ("RightForeArmRollLink", ("rightforearmroll", "rightforearmtwist", "rforearmtwist")),
        ("RightHandLink", ("righthand", "rwrist")),
        ("LeftUpLegRollLink", ("leftuplegroll", "leftthightwist", "lthightwist")),
        ("LeftLegRollLink", ("leftlegroll", "leftcalftwist", "lcalftwist")),
        ("RightUpLegRollLink", ("rightuplegroll", "rightthightwist", "rthightwist")),
        ("RightLegRollLink", ("rightlegroll", "rightcalftwist", "rcalftwist")),
        ("LeftHandThumb1Link", ("lefthandthumb1", "lthumb1")),
        ("LeftHandThumb2Link", ("lefthandthumb2", "lthumb2")),
        ("LeftHandThumb3Link", ("lefthandthumb3", "lthumb3")),
        ("LeftHandThumb4Link", ("lefthandthumb4", "lthumb4")),
        ("LeftHandIndex1Link", ("lefthandindex1", "lindex1")),
        ("LeftHandIndex2Link", ("lefthandindex2", "lindex2")),
        ("LeftHandIndex3Link", ("lefthandindex3", "lindex3")),
        ("LeftHandIndex4Link", ("lefthandindex4", "lindex4")),
        ("LeftHandMiddle1Link", ("lefthandmiddle1", "lmiddle1")),
        ("LeftHandMiddle2Link", ("lefthandmiddle2", "lmiddle2")),
        ("LeftHandMiddle3Link", ("lefthandmiddle3", "lmiddle3")),
        ("LeftHandMiddle4Link", ("lefthandmiddle4", "lmiddle4")),
        ("LeftHandRing1Link", ("lefthandring1", "lring1")),
        ("LeftHandRing2Link", ("lefthandring2", "lring2")),
        ("LeftHandRing3Link", ("lefthandring3", "lring3")),
        ("LeftHandRing4Link", ("lefthandring4", "lring4")),
        ("LeftHandPinky1Link", ("lefthandpinky1", "lpinky1")),
        ("LeftHandPinky2Link", ("lefthandpinky2", "lpinky2")),
        ("LeftHandPinky3Link", ("lefthandpinky3", "lpinky3")),
        ("LeftHandPinky4Link", ("lefthandpinky4", "lpinky4")),
        ("RightHandThumb1Link", ("righthandthumb1", "rthumb1")),
        ("RightHandThumb2Link", ("righthandthumb2", "rthumb2")),
        ("RightHandThumb3Link", ("righthandthumb3", "rthumb3")),
        ("RightHandThumb4Link", ("righthandthumb4", "rthumb4")),
        ("RightHandIndex1Link", ("righthandindex1", "rindex1")),
        ("RightHandIndex2Link", ("righthandindex2", "rindex2")),
        ("RightHandIndex3Link", ("righthandindex3", "rindex3")),
        ("RightHandIndex4Link", ("righthandindex4", "rindex4")),
        ("RightHandMiddle1Link", ("righthandmiddle1", "rmiddle1")),
        ("RightHandMiddle2Link", ("righthandmiddle2", "rmiddle2")),
        ("RightHandMiddle3Link", ("righthandmiddle3", "rmiddle3")),
        ("RightHandMiddle4Link", ("righthandmiddle4", "rmiddle4")),
        ("RightHandRing1Link", ("righthandring1", "rring1")),
        ("RightHandRing2Link", ("righthandring2", "rring2")),
        ("RightHandRing3Link", ("righthandring3", "rring3")),
        ("RightHandRing4Link", ("righthandring4", "rring4")),
        ("RightHandPinky1Link", ("righthandpinky1", "rpinky1")),
        ("RightHandPinky2Link", ("righthandpinky2", "rpinky2")),
        ("RightHandPinky3Link", ("righthandpinky3", "rpinky3")),
        ("RightHandPinky4Link", ("righthandpinky4", "rpinky4")),
    ]
)

_TOOL = None
_QT_TOOL = None
_QT_DOCK = None
_QT_LAUNCHER_TOOLBAR = None
_QT_LAUNCHER_ACTION = None
_TOAST = None
_TOAST_QUEUE = []
_TOAST_ACTIVE = False
_WARNING_LAST_SHOWN = {}
_WARNING_HISTORY = []
_STATUS_LINES = []
_CALLBACKS_INSTALLED = False
_PROP_MARKER_BASE_NAME = DEFAULT_PROP_MARKER_BASE_NAME
_ACTIVE_THEME = DEFAULT_THEME_KEY
_APP_THEME_BASELINE = None
_APP_THEME_OWNED = False
_APP_THEME_BASELINE_PALETTE = None
_APP_THEME_BASELINE_STYLE = None


def _now():
    return time.time()


def _safe_caption(text):
    return str(text or "").strip()


def _component_short_name(component):
    if component is None:
        return ""
    return str(getattr(component, "Name", "") or getattr(component, "LongName", "") or "")


def _component_long_name(component):
    if component is None:
        return ""
    return str(getattr(component, "LongName", "") or getattr(component, "Name", "") or "")


def _namespace_from_long_name(long_name):
    text = str(long_name or "")
    if ":" not in text:
        return ""
    return text.split(":", 1)[0]


def _short_name_from_long_name(long_name):
    text = str(long_name or "")
    if ":" not in text:
        return text
    return text.split(":")[-1]


def _normalize_name(name):
    return re.sub(r"[^a-z0-9]+", "", str(name or "").lower())


def _sanitize_prop_marker_base_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(name or "").strip()).strip("_")
    return cleaned or DEFAULT_PROP_MARKER_BASE_NAME


def get_prop_marker_base_name():
    return _PROP_MARKER_BASE_NAME


def set_prop_marker_base_name(name):
    global _PROP_MARKER_BASE_NAME
    clean_name = _sanitize_prop_marker_base_name(name)
    _PROP_MARKER_BASE_NAME = clean_name
    return clean_name


def _is_dummy_name(name):
    clean = _normalize_name(name)
    return clean.endswith("dummy") or clean.endswith("end")


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


def _qt_host_main_window():
    if QtWidgets is None:
        return None
    app = QtWidgets.QApplication.instance()
    if app is None:
        return None
    for widget in app.topLevelWidgets():
        try:
            if hasattr(widget, "addDockWidget") and "MotionBuilder" in (widget.windowTitle() or ""):
                return widget
        except Exception:
            continue
    active = app.activeWindow()
    if active is not None and hasattr(active, "addDockWidget"):
        return active
    return None


def _existing_aminate_mobu_docks():
    if QtWidgets is None:
        return []
    main = _qt_host_main_window()
    if main is None:
        return []
    docks = []
    for widget in main.findChildren(QtWidgets.QDockWidget):
        try:
            if widget.objectName() == QT_DOCK_OBJECT_NAME:
                docks.append(widget)
        except Exception:
            continue
    return docks


def _close_duplicate_aminate_mobu_docks(keep_dock=None):
    for widget in _existing_aminate_mobu_docks():
        if keep_dock is not None and widget is keep_dock:
            continue
        try:
            widget.close()
        except Exception:
            pass
        try:
            widget.deleteLater()
        except Exception:
            pass


def _existing_aminate_launcher_toolbars():
    if QtWidgets is None:
        return []
    main = _qt_host_main_window()
    if main is None:
        return []
    toolbars = []
    for widget in main.findChildren(QtWidgets.QToolBar):
        try:
            if widget.objectName() == QT_LAUNCHER_TOOLBAR_OBJECT_NAME:
                toolbars.append(widget)
        except Exception:
            continue
    return toolbars


def _close_duplicate_aminate_launcher_toolbars(keep_toolbar=None):
    for widget in _existing_aminate_launcher_toolbars():
        if keep_toolbar is not None and widget is keep_toolbar:
            continue
        try:
            widget.hide()
        except Exception:
            pass
        try:
            widget.deleteLater()
        except Exception:
            pass


def _qt_application():
    if QtWidgets is None:
        return None
    return QtWidgets.QApplication.instance()


def _copy_palette(palette):
    if QtGui is None or palette is None:
        return None
    try:
        return QtGui.QPalette(palette)
    except Exception:
        return None


def _make_modern_dark_palette():
    if QtGui is None:
        return None
    palette = QtGui.QPalette()
    colors = {
        QtGui.QPalette.Window: QtGui.QColor("#454545"),
        QtGui.QPalette.WindowText: QtGui.QColor("#E4E7EA"),
        QtGui.QPalette.Base: QtGui.QColor("#2B2E31"),
        QtGui.QPalette.AlternateBase: QtGui.QColor("#383C40"),
        QtGui.QPalette.ToolTipBase: QtGui.QColor("#383C40"),
        QtGui.QPalette.ToolTipText: QtGui.QColor("#EEF1F3"),
        QtGui.QPalette.Text: QtGui.QColor("#E4E7E9"),
        QtGui.QPalette.Button: QtGui.QColor("#494D52"),
        QtGui.QPalette.ButtonText: QtGui.QColor("#EEF1F3"),
        QtGui.QPalette.BrightText: QtGui.QColor("#FFFFFF"),
        QtGui.QPalette.Highlight: QtGui.QColor("#6D8293"),
        QtGui.QPalette.HighlightedText: QtGui.QColor("#F0F2F4"),
        QtGui.QPalette.Light: QtGui.QColor("#5A5F64"),
        QtGui.QPalette.Midlight: QtGui.QColor("#52575C"),
        QtGui.QPalette.Mid: QtGui.QColor("#4A4F54"),
        QtGui.QPalette.Dark: QtGui.QColor("#26282A"),
        QtGui.QPalette.Shadow: QtGui.QColor("#1B1D1F"),
        QtGui.QPalette.Link: QtGui.QColor("#8BA0AE"),
        QtGui.QPalette.LinkVisited: QtGui.QColor("#A4B3BE"),
        QtGui.QPalette.PlaceholderText: QtGui.QColor("#8F979F"),
    }
    for role, color in colors.items():
        try:
            palette.setColor(role, color)
        except Exception:
            pass
    try:
        disabled_text = QtGui.QColor("#737B82")
        disabled_bg = QtGui.QColor("#252729")
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, disabled_bg)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, disabled_bg)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor("#303234"))
    except Exception:
        pass
    return palette


def _refresh_qt_theme():
    app = _qt_application()
    if app is None:
        return False
    try:
        app.processEvents()
    except Exception:
        pass
    widgets = []
    try:
        widgets = list(app.topLevelWidgets())
    except Exception:
        widgets = []
    for widget in widgets:
        try:
            style = widget.style()
            if style is not None:
                style.unpolish(widget)
                style.polish(widget)
            widget.update()
            widget.repaint()
        except Exception:
            continue
    try:
        app.processEvents()
    except Exception:
        pass
    return True


def _normalize_theme_key(theme_key):
    return theme_key if theme_key in THEME_LABELS else DEFAULT_THEME_KEY


def get_active_theme():
    return _normalize_theme_key(_ACTIVE_THEME)


def set_active_theme(theme_key):
    global _ACTIVE_THEME
    _ACTIVE_THEME = _normalize_theme_key(theme_key)
    return _ACTIVE_THEME


def _other_theme(theme_key):
    theme_key = _normalize_theme_key(theme_key)
    return THEME_MODERN if theme_key == THEME_MOTIONBUILDER else THEME_MOTIONBUILDER


def _theme_label(theme_key):
    return THEME_LABELS[_normalize_theme_key(theme_key)]


def _theme_toggle_caption(theme_key):
    return "Switch to {0} UI".format(_theme_label(_other_theme(theme_key)))


def _theme_tooltip(theme_key):
    return "Current theme: {0}. Click to switch to {1}.".format(
        _theme_label(theme_key),
        _theme_label(_other_theme(theme_key)),
    )


def _theme_stylesheet(theme_key):
    return AMINATE_MOBU_LOCAL_STYLESHEETS[_normalize_theme_key(theme_key)]


def _app_theme_stylesheet(theme_key):
    return APP_THEME_STYLESHEETS[_normalize_theme_key(theme_key)]


def _restore_app_theme():
    global _APP_THEME_BASELINE, _APP_THEME_OWNED, _APP_THEME_BASELINE_PALETTE, _APP_THEME_BASELINE_STYLE
    app = _qt_application()
    if app is None or not _APP_THEME_OWNED:
        return False
    try:
        if _APP_THEME_BASELINE_STYLE:
            app.setStyle(_APP_THEME_BASELINE_STYLE)
    except Exception:
        pass
    try:
        if _APP_THEME_BASELINE_PALETTE is not None:
            app.setPalette(_APP_THEME_BASELINE_PALETTE)
    except Exception:
        pass
    app.setStyleSheet(_APP_THEME_BASELINE or "")
    _APP_THEME_OWNED = False
    _refresh_qt_theme()
    return True


def _apply_app_theme(theme_key):
    global _APP_THEME_BASELINE, _APP_THEME_OWNED, _APP_THEME_BASELINE_PALETTE, _APP_THEME_BASELINE_STYLE
    app = _qt_application()
    if app is None:
        return False
    theme_key = _normalize_theme_key(theme_key)
    if _APP_THEME_BASELINE is None:
        _APP_THEME_BASELINE = app.styleSheet()
    if _APP_THEME_BASELINE_PALETTE is None:
        _APP_THEME_BASELINE_PALETTE = _copy_palette(app.palette())
    if _APP_THEME_BASELINE_STYLE is None:
        try:
            _APP_THEME_BASELINE_STYLE = app.style().objectName()
        except Exception:
            _APP_THEME_BASELINE_STYLE = None
    if theme_key == THEME_MOTIONBUILDER:
        try:
            if _APP_THEME_BASELINE_STYLE:
                app.setStyle(_APP_THEME_BASELINE_STYLE)
        except Exception:
            pass
        try:
            if _APP_THEME_BASELINE_PALETTE is not None:
                app.setPalette(_APP_THEME_BASELINE_PALETTE)
        except Exception:
            pass
        app.setStyleSheet(_APP_THEME_BASELINE or "")
        _APP_THEME_OWNED = False
        _refresh_qt_theme()
        return True
    try:
        app.setStyle("Fusion")
    except Exception:
        pass
    palette = _make_modern_dark_palette()
    if palette is not None:
        try:
            app.setPalette(palette)
        except Exception:
            pass
    app.setStyleSheet(_app_theme_stylesheet(theme_key))
    _APP_THEME_OWNED = True
    _refresh_qt_theme()
    return True


def _style_donate_button(button, theme_key=None):
    if not button or not QtWidgets:
        return
    theme_key = _normalize_theme_key(theme_key)
    button.setMinimumWidth(92)
    if theme_key == THEME_MOTIONBUILDER:
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #D9A441;
                color: #1A1A1A;
                border: 1px solid #9A742B;
                border-radius: 3px;
                padding: 6px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E7B24A;
            }
            QPushButton:pressed {
                background-color: #C89232;
            }
            """
        )
        return
    button.setStyleSheet(
        """
        QPushButton {
            background-color: #F3C54A;
            color: #1B1B1B;
            border: 1px solid #DAAE37;
            border-radius: 10px;
            padding: 6px 14px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #F8D163;
        }
        QPushButton:pressed {
            background-color: #E2B53F;
        }
        """
    )


def _on_qt_panel_destroyed(*_args):
    global _QT_TOOL
    global _QT_DOCK
    _QT_TOOL = None
    _QT_DOCK = None
    _restore_app_theme()


def _ensure_aminate_launcher_toolbar():
    global _QT_LAUNCHER_TOOLBAR
    global _QT_LAUNCHER_ACTION
    if QtWidgets is None or QtCore is None:
        return None
    main = _qt_host_main_window()
    if main is None or not hasattr(main, "addToolBar"):
        return None
    if _QT_LAUNCHER_TOOLBAR is None:
        existing = _existing_aminate_launcher_toolbars()
        if existing:
            _QT_LAUNCHER_TOOLBAR = existing[-1]
            _close_duplicate_aminate_launcher_toolbars(keep_toolbar=_QT_LAUNCHER_TOOLBAR)
    if _QT_LAUNCHER_TOOLBAR is None:
        toolbar = QtWidgets.QToolBar("Aminate")
        toolbar.setObjectName(QT_LAUNCHER_TOOLBAR_OBJECT_NAME)
        toolbar.setMovable(True)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        action = toolbar.addAction("Aminate")
        try:
            action.triggered.connect(lambda _checked=False: launch_aminate_mobu())
        except Exception:
            pass
        widget = toolbar.widgetForAction(action)
        if widget is not None:
            widget.setObjectName(QT_LAUNCHER_BUTTON_OBJECT_NAME)
            widget.setToolTip("Open the dockable Aminate Mobu tools.")
        main.addToolBar(QtCore.Qt.TopToolBarArea, toolbar)
        _QT_LAUNCHER_TOOLBAR = toolbar
        _QT_LAUNCHER_ACTION = action
    else:
        action_list = list(_QT_LAUNCHER_TOOLBAR.actions())
        _QT_LAUNCHER_ACTION = action_list[0] if action_list else _QT_LAUNCHER_TOOLBAR.addAction("Aminate")
        widget = _QT_LAUNCHER_TOOLBAR.widgetForAction(_QT_LAUNCHER_ACTION)
        if widget is not None:
            widget.setObjectName(QT_LAUNCHER_BUTTON_OBJECT_NAME)
            widget.setToolTip("Open the dockable Aminate Mobu tools.")
    _close_duplicate_aminate_launcher_toolbars(keep_toolbar=_QT_LAUNCHER_TOOLBAR)
    try:
        _QT_LAUNCHER_TOOLBAR.show()
    except Exception:
        pass
    return _QT_LAUNCHER_TOOLBAR


def ensure_motionbuilder_ui_entry():
    return _ensure_aminate_launcher_toolbar()


def discover_motionbuilder_startup_dirs(root_dir=None):
    root_dir = root_dir or MB_DOCUMENTS_ROOT
    if not os.path.isdir(root_dir):
        return []
    startup_dirs = []
    for entry in sorted(os.listdir(root_dir), reverse=True):
        version_root = os.path.join(root_dir, entry)
        if not os.path.isdir(version_root):
            continue
        if not entry.isdigit():
            continue
        startup_dir = os.path.join(version_root, "config", "PythonStartup")
        startup_dirs.append(startup_dir)
    return startup_dirs


def startup_bootstrap_path(startup_dir=None):
    if startup_dir:
        return os.path.join(startup_dir, STARTUP_BOOTSTRAP_FILENAME)
    startup_dirs = discover_motionbuilder_startup_dirs()
    target_dir = startup_dirs[0] if startup_dirs else os.path.join(MB_DOCUMENTS_ROOT, "2026", "config", "PythonStartup")
    return os.path.join(target_dir, STARTUP_BOOTSTRAP_FILENAME)


def install_motionbuilder_startup(startup_dir=None, module_root=None):
    module_root = module_root or os.path.dirname(os.path.abspath(__file__))
    target_dirs = [startup_dir] if startup_dir else discover_motionbuilder_startup_dirs()
    if not target_dirs:
        target_dirs = [os.path.join(MB_DOCUMENTS_ROOT, "2026", "config", "PythonStartup")]
    bootstrap = """from __future__ import absolute_import, division, print_function
import importlib
import sys
MODULE_ROOT = r\"{module_root}\"
if MODULE_ROOT not in sys.path:
    sys.path.insert(0, MODULE_ROOT)
def _boot():
    import aminate_mobu
    importlib.reload(aminate_mobu)
    aminate_mobu.ensure_motionbuilder_ui_entry()
try:
    from PySide6 import QtCore
except Exception:
    try:
        from PySide2 import QtCore
    except Exception:
        QtCore = None
if QtCore is not None:
    QtCore.QTimer.singleShot(250, _boot)
else:
    _boot()
""".format(module_root=module_root.replace("\\", "\\\\"))
    installed_paths = []
    for target_dir in target_dirs:
        os.makedirs(target_dir, exist_ok=True)
        bootstrap_path = startup_bootstrap_path(target_dir)
        with open(bootstrap_path, "w", encoding="utf-8") as handle:
            handle.write(bootstrap)
        installed_paths.append(bootstrap_path)
    return installed_paths


def _open_external_url(url):
    if not url:
        return False
    if QtGui and hasattr(QtGui, "QDesktopServices"):
        return QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
    return False


class _ToastWidget(QtWidgets.QFrame if QtWidgets else object):
    def __init__(self):
        super(_ToastWidget, self).__init__(None)
        flags = QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setObjectName("AminateMobuToast")
        self.setStyleSheet(
            "#AminateMobuToast { background: rgba(18, 24, 31, 230); border: 1px solid rgba(114, 184, 255, 180); border-radius: 10px; }"
            "QLabel { color: white; font-size: 13px; padding: 10px 14px; }"
        )
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._label = QtWidgets.QLabel("")
        self._label.setWordWrap(True)
        self._layout.addWidget(self._label)
        self._hide_timer = QtCore.QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)
        self._animation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        self._animation.setDuration(220)
        self._animation.finished.connect(self._after_hide)
        self._done = None

    def show_message(self, message, duration_ms, done_callback):
        self._done = done_callback
        self._animation.stop()
        self._hide_timer.stop()
        self._label.setText(str(message or ""))
        self.adjustSize()
        self._position()
        self.setWindowOpacity(1.0)
        self.show()
        self.raise_()
        self._hide_timer.start(int(duration_ms))

    def _position(self):
        anchor = _qt_host_main_window() or _qt_main_window()
        if anchor is None:
            return
        geo = anchor.frameGeometry()
        self.adjustSize()
        x_pos = geo.x() + int((geo.width() - self.width()) / 2)
        y_pos = geo.y() + geo.height() - self.height() - 56
        self.move(x_pos, y_pos)

    def _fade_out(self):
        self._animation.stop()
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _after_hide(self):
        self.hide()
        self.setWindowOpacity(1.0)
        done = self._done
        self._done = None
        if done:
            done()


def _ensure_toast():
    global _TOAST
    if QtWidgets is None:
        return None
    if _TOAST is None:
        _TOAST = _ToastWidget()
    return _TOAST


def _toast_finished():
    global _TOAST_ACTIVE
    _TOAST_ACTIVE = False
    _show_next_toast()


def _show_next_toast():
    global _TOAST_ACTIVE
    if _TOAST_ACTIVE or not _TOAST_QUEUE:
        return
    widget = _ensure_toast()
    if widget is None:
        _TOAST_QUEUE[:] = []
        return
    kind, message, duration_ms = _TOAST_QUEUE.pop(0)
    _TOAST_ACTIVE = True
    widget.show_message(message, duration_ms, _toast_finished)


def _warning_allowed(kind, throttle_seconds):
    now = _now()
    last_shown = _WARNING_LAST_SHOWN.get(kind, 0.0)
    if now - last_shown < float(throttle_seconds):
        return False
    _WARNING_LAST_SHOWN[kind] = now
    return True


def _record_warning(kind, message):
    payload = {"kind": str(kind), "message": str(message), "time": _now()}
    _WARNING_HISTORY.append(payload)
    return payload


def _queue_warning(kind, message, duration_ms=DEFAULT_TOAST_DURATION_MS, throttle_seconds=0.0):
    if throttle_seconds and not _warning_allowed(kind, throttle_seconds):
        return False
    _record_warning(kind, message)
    widget = _ensure_toast()
    if widget is not None:
        _TOAST_QUEUE.append((kind, message, duration_ms))
        _show_next_toast()
    else:
        print("[Aminate Mobu][{0}] {1}".format(kind, message))
    return True


def reset_runtime_state(clear_tool=False):
    global _QT_TOOL
    global _QT_DOCK
    global _QT_LAUNCHER_TOOLBAR
    global _QT_LAUNCHER_ACTION
    global _TOAST_QUEUE, _TOAST_ACTIVE, _WARNING_LAST_SHOWN, _WARNING_HISTORY, _STATUS_LINES
    _TOAST_QUEUE = []
    _TOAST_ACTIVE = False
    _WARNING_LAST_SHOWN = {}
    _WARNING_HISTORY = []
    _STATUS_LINES = []
    remove_runtime_watchers()
    if clear_tool:
        _restore_app_theme()
        _close_duplicate_aminate_mobu_docks()
        _close_duplicate_aminate_launcher_toolbars(keep_toolbar=_QT_LAUNCHER_TOOLBAR)
    if clear_tool and _QT_DOCK is not None:
        try:
            _QT_DOCK.close()
        except Exception:
            pass
        try:
            _QT_DOCK.deleteLater()
        except Exception:
            pass
        _QT_DOCK = None
    if clear_tool and _QT_TOOL is not None:
        try:
            _QT_TOOL.close()
        except Exception:
            pass
        try:
            _QT_TOOL.deleteLater()
        except Exception:
            pass
        _QT_TOOL = None
    if clear_tool and _QT_LAUNCHER_TOOLBAR is not None:
        try:
            _QT_LAUNCHER_TOOLBAR.hide()
        except Exception:
            pass
        try:
            _QT_LAUNCHER_TOOLBAR.deleteLater()
        except Exception:
            pass
        _QT_LAUNCHER_TOOLBAR = None
        _QT_LAUNCHER_ACTION = None
    if clear_tool and TOOL_NAME in pyfbsdk_additions.FBToolList:
        pyfbsdk_additions.FBDestroyToolByName(TOOL_NAME)


def get_warning_history():
    return list(_WARNING_HISTORY)


def _set_status_lines(lines):
    global _STATUS_LINES
    _STATUS_LINES = [str(line) for line in lines if str(line).strip()]
    memo = getattr(_TOOL, "status_memo", None)
    if memo is not None:
        text = FBStringList()
        for line in _STATUS_LINES:
            text.Add(line)
        memo.SetStrings(text)
    qt_memo = getattr(_QT_TOOL, "status_memo", None)
    if qt_memo is not None:
        qt_memo.setPlainText("\n".join(_STATUS_LINES))
    qt_status = getattr(_QT_TOOL, "status_label", None)
    if qt_status is not None:
        qt_status.setText(_STATUS_LINES[-1] if _STATUS_LINES else "Ready.")


def _append_status(line):
    lines = list(_STATUS_LINES)
    lines.append(str(line))
    _set_status_lines(lines[-28:])


def _property_src_count(prop):
    try:
        return int(prop.GetSrcCount())
    except Exception:
        return 0


def _property_first_src(prop):
    try:
        return prop.GetSrc(0)
    except Exception:
        return None


def _character_summary(character):
    if character is None:
        return "Current Character: none"
    return "Current Character: {0} | Characterized: {1} | Keying Mode: {2}".format(
        character.LongName,
        bool(character.GetCharacterize()),
        character.KeyingMode,
    )


def _selected_models():
    models = FBModelList()
    FBGetSelectedModels(models)
    return list(models)


def _current_character():
    return FBApplication().CurrentCharacter


def _scene_models(predicate=None):
    output = []
    for component in FBSystem().Scene.Components:
        if isinstance(component, FBModel):
            if predicate is None or predicate(component):
                output.append(component)
    return output


def _scene_skeletons(namespace=None):
    output = []
    for model in _scene_models(lambda item: isinstance(item, FBModelSkeleton)):
        if namespace and _namespace_from_long_name(model.LongName) != namespace:
            continue
        output.append(model)
    return output


def _scene_markers():
    return _scene_models(lambda item: isinstance(item, (FBModelMarker, FBModelMarkerOptical)))


def _is_unlabelled_marker(marker):
    short_name = _short_name_from_long_name(_component_long_name(marker))
    return bool(UNLABELLED_MARKER_PATTERN.match(short_name))


def _property_has_animation_keys(prop):
    if prop is None:
        return False
    try:
        animation_node = prop.GetAnimationNode()
    except Exception:
        animation_node = None
    if animation_node is None:
        return False
    for child in getattr(animation_node, "Nodes", []) or []:
        fcurve = getattr(child, "FCurve", None)
        if fcurve is None:
            continue
        try:
            if len(fcurve.Keys) > 0:
                return True
        except Exception:
            continue
    return False


def _marker_has_transform_animation(marker):
    if marker is None:
        return False
    for prop_name in CONTROL_RIG_PROPERTY_NAMES:
        prop = marker.PropertyList.Find(prop_name)
        if _property_has_animation_keys(prop):
            return True
    return False


def _existing_component_short_names():
    names = set()
    for component in FBSystem().Scene.Components:
        name = _short_name_from_long_name(_component_long_name(component))
        if name:
            names.add(name)
    return names


def _rename_component(component, target_name):
    old_name = _component_long_name(component)
    try:
        component.Name = target_name
    except Exception:
        return "", old_name
    return _component_long_name(component), old_name


def _rename_prop_markers(markers, base_name):
    renamed = []
    existing_names = _existing_component_short_names()
    sorted_markers = sorted(markers or [], key=lambda item: _component_long_name(item))
    clean_base_name = _sanitize_prop_marker_base_name(base_name)
    counter = 1
    for marker in sorted_markers:
        original_name = _short_name_from_long_name(_component_long_name(marker))
        while True:
            candidate = "{0}_{1}".format(clean_base_name, counter)
            counter += 1
            if candidate == original_name or candidate not in existing_names:
                break
        new_long_name, old_long_name = _rename_component(marker, candidate)
        new_short_name = _short_name_from_long_name(new_long_name or candidate)
        existing_names.discard(original_name)
        existing_names.add(new_short_name)
        renamed.append({"from": old_long_name, "to": new_long_name or candidate})
    return renamed


def collect_scene_clean_targets():
    cameras = []
    for camera in FBSystem().Scene.Cameras:
        short_name = _short_name_from_long_name(_component_long_name(camera))
        if short_name.startswith("Producer "):
            continue
        cameras.append(camera)
    junk_markers = []
    prop_markers = []
    for marker in _scene_markers():
        if not _is_unlabelled_marker(marker):
            continue
        if _marker_has_transform_animation(marker):
            prop_markers.append(marker)
        else:
            junk_markers.append(marker)
    return cameras, junk_markers, prop_markers


def delete_components(components):
    deleted = []
    for component in components:
        long_name = _component_long_name(component)
        try:
            component.FBDelete()
            deleted.append(long_name)
        except Exception:
            pass
    return deleted


def run_scene_cleaner(delete_cameras=True, delete_unlabelled_markers=True, prop_marker_base_name=None):
    clean_base_name = set_prop_marker_base_name(prop_marker_base_name or get_prop_marker_base_name())
    cameras, junk_markers, prop_markers = collect_scene_clean_targets()
    deleted_cameras = delete_components(cameras) if delete_cameras else []
    renamed_markers = _rename_prop_markers(prop_markers, clean_base_name) if delete_unlabelled_markers else []
    deleted_markers = delete_components(junk_markers) if delete_unlabelled_markers else []
    result = {
        "deleted_cameras": deleted_cameras,
        "deleted_markers": deleted_markers,
        "renamed_markers": renamed_markers,
        "preserved_prop_markers": [item.get("to") for item in renamed_markers],
        "prop_marker_base_name": clean_base_name,
        "camera_count": len(deleted_cameras),
        "marker_count": len(deleted_markers),
        "renamed_marker_count": len(renamed_markers),
    }
    _append_status(
        "Scene Cleaner deleted {0} user camera(s), deleted {1} junk marker(s), and renamed {2} animated prop marker(s) with base {3}.".format(
            len(deleted_cameras),
            len(deleted_markers),
            len(renamed_markers),
            clean_base_name,
        )
    )
    return result


def _candidate_namespace_from_selection():
    for model in _selected_models():
        if isinstance(model, FBModelSkeleton):
            return _namespace_from_long_name(model.LongName)
    return ""


def _index_namespace_skeletons(namespace):
    indexed = OrderedDict()
    for model in _scene_skeletons(namespace=namespace):
        short_name = _short_name_from_long_name(model.LongName)
        if _is_dummy_name(short_name):
            continue
        normalized = _normalize_name(short_name)
        indexed.setdefault(normalized, model)
    return indexed


def _slot_match_for_index(slot_name, indexed):
    for candidate in CHARACTER_SLOT_CANDIDATES.get(slot_name, ()):
        model = indexed.get(_normalize_name(candidate))
        if model is not None:
            return model
    return None


def _available_namespaces():
    namespaces = OrderedDict()
    for model in _scene_skeletons():
        namespaces.setdefault(_namespace_from_long_name(model.LongName), True)
    return list(namespaces.keys())


def _namespace_score(namespace):
    indexed = _index_namespace_skeletons(namespace)
    score = 0
    for slot_name in CORE_REQUIRED_LINKS:
        if _slot_match_for_index(slot_name, indexed):
            score += 1
    return score, indexed


def find_best_skeleton_namespace():
    preferred = _candidate_namespace_from_selection()
    candidates = _available_namespaces()
    if preferred and preferred in candidates:
        candidates = [preferred] + [item for item in candidates if item != preferred]
    best_namespace = ""
    best_score = -1
    best_index = OrderedDict()
    for namespace in candidates:
        score, indexed = _namespace_score(namespace)
        if score > best_score:
            best_namespace = namespace
            best_score = score
            best_index = indexed
    return best_namespace, best_index, best_score


def _unique_character_name(base_name):
    existing = {_component_short_name(character) for character in FBSystem().Scene.Characters}
    if base_name not in existing:
        return base_name
    counter = 1
    while True:
        candidate = "{0}_{1}".format(base_name, counter)
        if candidate not in existing:
            return candidate
        counter += 1


def _map_model_to_slot(character, slot_name, model):
    prop = character.PropertyList.Find(slot_name, False)
    if prop is None or model is None:
        return False
    try:
        prop.append(model)
        return True
    except Exception:
        try:
            prop.ConnectSrc(model)
            return True
        except Exception:
            return False


def _core_link_count(character):
    count = 0
    for slot_name in CORE_REQUIRED_LINKS:
        prop = character.PropertyList.Find(slot_name, False)
        if prop and _property_src_count(prop) > 0:
            count += 1
    return count


def character_setup_seems_done(character):
    return _core_link_count(character) >= len(CORE_REQUIRED_LINKS)


def maybe_warn_lock_definition(character):
    if character is None:
        return False
    if character.GetCharacterize():
        return False
    if not character_setup_seems_done(character):
        return False
    return _queue_warning(
        "lock_definition",
        LOCK_DEFINITION_WARNING,
        duration_ms=DEFAULT_TOAST_DURATION_MS,
        throttle_seconds=LOCK_WARNING_THROTTLE_SECONDS,
    )


def _control_rig_model_names(character):
    names = set()
    if character is None:
        return names
    for body_node in FBBodyNodeId.values.values():
        try:
            model = character.GetCtrlRigModel(body_node)
        except Exception:
            model = None
        if model is not None:
            names.add(_component_long_name(model))
    return names


def maybe_warn_control_rig_mode(character, model, property_name):
    if character is None or model is None:
        return False
    if str(property_name or "") not in CONTROL_RIG_PROPERTY_NAMES:
        return False
    if character.KeyingMode in (
        FBCharacterKeyingMode.kFBCharacterKeyingBodyPart,
        FBCharacterKeyingMode.kFBCharacterKeyingFullBody,
    ):
        return False
    if _component_long_name(model) not in _control_rig_model_names(character):
        return False
    return _queue_warning(
        "control_rig_mode",
        CONTROL_RIG_MODE_WARNING,
        duration_ms=DEFAULT_TOAST_DURATION_MS,
        throttle_seconds=MODE_WARNING_THROTTLE_SECONDS,
    )


def auto_map_character(create_control_rig=True, characterize=True, activate_input=False):
    namespace, indexed, score = find_best_skeleton_namespace()
    if score <= 0:
        result = {"ok": False, "error": "No usable skeleton namespace found.", "namespace": namespace}
        _append_status(result["error"])
        return result
    namespace_label = namespace or "Scene"
    character_name = _unique_character_name("AminateMobu_{0}".format(namespace_label.replace(":", "_") or "Character"))
    character = FBCharacter(character_name)
    FBApplication().CurrentCharacter = character
    mapped = OrderedDict()
    for slot_name in CHARACTER_SLOT_CANDIDATES:
        model = _slot_match_for_index(slot_name, indexed)
        if model is None:
            continue
        if slot_name == "HipsTranslationLink" and _component_long_name(model) == mapped.get("HipsLink", ""):
            continue
        if _map_model_to_slot(character, slot_name, model):
            mapped[slot_name] = _component_long_name(model)
    characterize_result = None
    characterize_error = None
    control_rig_result = None
    if characterize:
        characterize_result = bool(character.SetCharacterizeOn(True))
        characterize_error = character.GetCharacterizeError()
    if create_control_rig and character.GetCharacterize():
        try:
            control_rig_result = bool(character.CreateControlRig(True))
        except Exception as exc:
            control_rig_result = False
            characterize_error = str(exc)
    if activate_input and character.GetCharacterize():
        try:
            character.ActiveInput = True
        except Exception:
            pass
    maybe_warn_lock_definition(character)
    result = {
        "ok": True,
        "namespace": namespace,
        "score": score,
        "character_name": character.LongName,
        "mapped_slots": dict(mapped),
        "mapped_count": len(mapped),
        "core_link_count": _core_link_count(character),
        "characterized": bool(character.GetCharacterize()),
        "characterize_result": characterize_result,
        "characterize_error": characterize_error,
        "control_rig_result": control_rig_result,
    }
    _append_status(
        "Auto Map created {0} from {1} with {2} mapped slot(s). Characterized: {3}.".format(
            character.LongName,
            namespace_label,
            len(mapped),
            bool(character.GetCharacterize()),
        )
    )
    return result


def validate_current_character():
    character = _current_character()
    if character is None:
        result = {"ok": False, "error": "No current character."}
        _append_status(result["error"])
        return result
    current_control_set = None
    try:
        current_control_set = character.GetCurrentControlSet()
    except Exception:
        current_control_set = None
    lock_warning = maybe_warn_lock_definition(character)
    result = {
        "ok": True,
        "character_name": character.LongName,
        "characterized": bool(character.GetCharacterize()),
        "core_link_count": _core_link_count(character),
        "has_control_set": bool(current_control_set),
        "keying_mode": str(character.KeyingMode),
        "lock_warning": bool(lock_warning),
    }
    _append_status(
        "Validate Character: {0} | Characterized {1} | Control Rig {2} | Keying {3}".format(
            character.LongName,
            bool(character.GetCharacterize()),
            bool(current_control_set),
            character.KeyingMode,
        )
    )
    return result


def set_keying_mode_body_part():
    character = _current_character()
    if character is None:
        return False
    character.KeyingMode = FBCharacterKeyingMode.kFBCharacterKeyingBodyPart
    _append_status("Keying mode switched to Body Part.")
    return True


def set_keying_mode_full_body():
    character = _current_character()
    if character is None:
        return False
    character.KeyingMode = FBCharacterKeyingMode.kFBCharacterKeyingFullBody
    _append_status("Keying mode switched to Full Body.")
    return True


def handle_transform_attempt(model, property_name):
    character = _current_character()
    return maybe_warn_control_rig_mode(character, model, property_name)


def _on_scene_change(control, event):
    character = _current_character()
    if character is not None:
        maybe_warn_lock_definition(character)


def _on_connection_data_notify(control, event):
    plug = getattr(event, "Plug", None)
    if plug is None:
        return
    property_name = ""
    try:
        property_name = plug.Name
    except Exception:
        try:
            property_name = plug.GetName()
        except Exception:
            property_name = ""
    if property_name not in CONTROL_RIG_PROPERTY_NAMES:
        return
    try:
        owner = plug.GetOwner()
    except Exception:
        owner = None
    if not isinstance(owner, FBModel):
        return
    maybe_warn_control_rig_mode(_current_character(), owner, property_name)


def _on_file_exit(control=None, event=None):
    _restore_app_theme()
    remove_runtime_watchers()


def install_runtime_watchers():
    global _CALLBACKS_INSTALLED
    if _CALLBACKS_INSTALLED:
        return
    system = FBSystem()
    app = FBApplication()
    system.Scene.OnChange.Add(_on_scene_change)
    system.OnConnectionDataNotify.Add(_on_connection_data_notify)
    app.OnFileExit.Add(_on_file_exit)
    _CALLBACKS_INSTALLED = True


def remove_runtime_watchers():
    global _CALLBACKS_INSTALLED
    if not _CALLBACKS_INSTALLED:
        return
    system = FBSystem()
    app = FBApplication()
    try:
        system.Scene.OnChange.Remove(_on_scene_change)
    except Exception:
        pass
    try:
        system.OnConnectionDataNotify.Remove(_on_connection_data_notify)
    except Exception:
        pass
    try:
        app.OnFileExit.Remove(_on_file_exit)
    except Exception:
        pass
    _CALLBACKS_INSTALLED = False


def _tool_intro_lines():
    return [
        TOOL_NAME + "  " + TOOL_VERSION,
        "",
        "Scene Cleaner removes user cameras, deletes junk default markers, and renames animated default markers as prop markers.",
        "History Timeline saves full-scene MotionBuilder snapshot branches beside the current scene.",
        SCENE_CLEANER_HINT,
        "",
        "Auto Map builds a MotionBuilder character from the best skeleton namespace and tries to characterize it all the way through fingers and extra spine links.",
        "",
        "If the character looks mapped but not locked, Aminate Mobu shows a lock-definition popup.",
        "If a control rig translate or rotate happens while keying mode is Selection, Aminate Mobu warns to use Body Part or Full Body.",
    ]


def _refresh_dashboard():
    character = _current_character()
    cameras, junk_markers, prop_markers = collect_scene_clean_targets()
    summary = [
        TOOL_NAME + "  " + TOOL_VERSION,
        _character_summary(character),
        "Scene Cleaner Targets: {0} camera(s)  {1} junk marker(s)  {2} prop marker(s)".format(
            len(cameras),
            len(junk_markers),
            len(prop_markers),
        ),
        "Prop Marker Base Name: {0}".format(get_prop_marker_base_name()),
        "Current Scene: {0}".format(FBApplication().FBXFileName or "Untitled"),
        "",
    ]
    summary.extend(_tool_intro_lines()[2:])
    summary.append("")
    summary.extend(_STATUS_LINES[-10:])
    _set_status_lines(summary)


def _button(caption, callback, color=None):
    button = FBButton()
    button.Caption = caption
    button.Look = FBButtonLook.kFBLookColorChange
    button.Style = FBButtonStyle.kFBPushButton
    button.Justify = FBTextJustify.kFBTextJustifyCenter
    if color is not None:
        button.SetStateColor(FBButtonState.kFBButtonState0, FBColor(*color))
    button.OnClick.Add(callback)
    return button


def _on_refresh(control=None, event=None):
    validate_current_character()
    _refresh_dashboard()


def _on_clean_scene(control=None, event=None, prop_marker_base_name=None):
    run_scene_cleaner(
        delete_cameras=True,
        delete_unlabelled_markers=True,
        prop_marker_base_name=prop_marker_base_name,
    )
    _refresh_dashboard()


def _on_clean_cameras(control=None, event=None):
    run_scene_cleaner(delete_cameras=True, delete_unlabelled_markers=False)
    _refresh_dashboard()


def _on_clean_markers(control=None, event=None, prop_marker_base_name=None):
    run_scene_cleaner(
        delete_cameras=False,
        delete_unlabelled_markers=True,
        prop_marker_base_name=prop_marker_base_name,
    )
    _refresh_dashboard()


def _on_auto_map(control=None, event=None):
    auto_map_character(create_control_rig=True, characterize=True, activate_input=False)
    _refresh_dashboard()


def _on_validate(control=None, event=None):
    validate_current_character()
    _refresh_dashboard()


def _on_body_part(control=None, event=None):
    set_keying_mode_body_part()
    _refresh_dashboard()


def _on_full_body(control=None, event=None):
    set_keying_mode_full_body()
    _refresh_dashboard()


def _on_history_timeline(control=None, event=None):
    import aminate_mobu_history

    aminate_mobu_history.launch_motionbuilder_history_timeline()
    _append_status("Opened Aminate Mobu History Timeline.")
    _refresh_dashboard()


if QtWidgets:
    class AminateMobuPanel(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super(AminateMobuPanel, self).__init__(parent)
            self.theme_key = get_active_theme()
            self.setObjectName(QT_WINDOW_OBJECT_NAME)
            self.setMinimumSize(860, 560)
            self.resize(920, 640)
            self._build_ui()
            self._apply_theme(self.theme_key)
            try:
                self.destroyed.connect(_on_qt_panel_destroyed)
            except Exception:
                pass

        def _build_ui(self):
            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setContentsMargins(8, 8, 8, 8)
            main_layout.setSpacing(8)
            header_layout = QtWidgets.QHBoxLayout()
            header_text_layout = QtWidgets.QVBoxLayout()
            header_text_layout.setSpacing(0)
            self.header_title = QtWidgets.QLabel(TOOL_NAME)
            self.header_title.setObjectName("aminateMobuHeaderTitle")
            header_text_layout.addWidget(self.header_title)
            self.header_subtitle = QtWidgets.QLabel("Scene cleanup  HIK mapping  setup warnings")
            self.header_subtitle.setObjectName("aminateMobuHeaderSubtitle")
            header_text_layout.addWidget(self.header_subtitle)
            header_layout.addLayout(header_text_layout, 1)
            self.theme_badge = QtWidgets.QLabel()
            self.theme_badge.setObjectName("aminateMobuThemeBadge")
            header_layout.addWidget(self.theme_badge)
            self.theme_button = QtWidgets.QPushButton()
            self.theme_button.setObjectName("aminateMobuThemeToggle")
            self.theme_button.clicked.connect(self._toggle_theme)
            header_layout.addWidget(self.theme_button)
            main_layout.addLayout(header_layout)
            main_layout.addWidget(
                self._build_intro_card(
                    "What This Tool Helps With",
                    "MotionBuilder companion for Aminate Maya. Clean scene junk, auto-map skeletons into HumanIK, warn before incomplete character setup, and launch full-scene History Timeline snapshots.",
                )
            )
            main_layout.addWidget(self._build_actions_group())
            main_layout.addWidget(self._build_note_group())
            self.status_label = QtWidgets.QLabel("Ready.")
            self.status_label.setObjectName("mayaAnimWorkflowStatusLabel")
            self.status_label.setWordWrap(True)
            main_layout.addWidget(self.status_label)
            self.status_memo = QtWidgets.QPlainTextEdit()
            self.status_memo.setReadOnly(True)
            self.status_memo.setObjectName("aminateMobuStatusMemo")
            main_layout.addWidget(self.status_memo, 1)
            footer_layout = QtWidgets.QHBoxLayout()
            self.brand_label = QtWidgets.QLabel(
                'Built by Amir. Follow Amir at <a href="{0}">followamir.com</a>.'.format(FOLLOW_AMIR_URL)
            )
            self.brand_label.setObjectName("mayaAnimWorkflowBrandLabel")
            self.brand_label.setOpenExternalLinks(False)
            self.brand_label.linkActivated.connect(self._open_follow_url)
            self.brand_label.setWordWrap(True)
            footer_layout.addWidget(self.brand_label, 1)
            self.version_label = QtWidgets.QLabel(TOOL_VERSION)
            self.version_label.setObjectName("mayaAnimWorkflowVersionLabel")
            footer_layout.addWidget(self.version_label)
            self.donate_button = QtWidgets.QPushButton("Donate")
            self.donate_button.setToolTip("Open Amir's PayPal donate link. Set AMIR_PAYPAL_DONATE_URL or AMIR_DONATE_URL to customize it.")
            self.donate_button.clicked.connect(self._open_donate_url)
            footer_layout.addWidget(self.donate_button)
            main_layout.addLayout(footer_layout)

        def _build_intro_card(self, title_text, body_text):
            frame = QtWidgets.QFrame()
            frame.setObjectName("mayaAnimWorkflowTabIntro")
            inner = QtWidgets.QVBoxLayout(frame)
            inner.setContentsMargins(10, 8, 10, 8)
            inner.setSpacing(4)
            title = QtWidgets.QLabel(title_text)
            title.setObjectName("mayaAnimWorkflowIntroTitle")
            body = QtWidgets.QLabel(body_text)
            body.setWordWrap(True)
            inner.addWidget(title)
            inner.addWidget(body)
            return frame

        def _build_actions_group(self):
            group = QtWidgets.QGroupBox("Actions")
            layout = QtWidgets.QVBoxLayout(group)
            layout.setSpacing(8)
            marker_row = QtWidgets.QHBoxLayout()
            marker_row.addWidget(QtWidgets.QLabel("Prop Marker Base Name"))
            self.prop_marker_base_field = QtWidgets.QLineEdit(get_prop_marker_base_name())
            self.prop_marker_base_field.setPlaceholderText(DEFAULT_PROP_MARKER_BASE_NAME)
            marker_row.addWidget(self.prop_marker_base_field, 1)
            layout.addLayout(marker_row)
            cleaner_grid = QtWidgets.QGridLayout()
            cleaner_grid.addWidget(self._action_button("Refresh", _on_refresh), 0, 0)
            cleaner_grid.addWidget(self._action_button("Scene Cleaner", self._run_scene_cleaner), 0, 1)
            cleaner_grid.addWidget(self._action_button("Delete Cameras", _on_clean_cameras), 0, 2)
            cleaner_grid.addWidget(self._action_button("Delete Markers", self._run_marker_cleanup), 0, 3)
            layout.addLayout(cleaner_grid)
            setup_grid = QtWidgets.QGridLayout()
            setup_grid.addWidget(self._action_button("Auto Map Skeleton", _on_auto_map), 0, 0)
            setup_grid.addWidget(self._action_button("Validate Character", _on_validate), 0, 1)
            setup_grid.addWidget(self._action_button("Body Part Mode", _on_body_part), 0, 2)
            setup_grid.addWidget(self._action_button("Full Body Mode", _on_full_body), 0, 3)
            layout.addLayout(setup_grid)
            history_row = QtWidgets.QHBoxLayout()
            history_row.addWidget(self._action_button("History Timeline", _on_history_timeline))
            history_row.addStretch(1)
            layout.addLayout(history_row)
            return group

        def _build_note_group(self):
            group = QtWidgets.QGroupBox("Notes")
            layout = QtWidgets.QVBoxLayout(group)
            hint = QtWidgets.QLabel(
                "Default markers with translation or rotation keys are treated as prop markers. Scene Cleaner keeps them, renames them with your chosen base name, and only deletes non-animated junk markers."
            )
            hint.setObjectName("aminateMobuGroupHint")
            hint.setWordWrap(True)
            layout.addWidget(hint)
            return group

        def _action_button(self, caption, callback):
            button = QtWidgets.QPushButton(caption)
            button.clicked.connect(lambda _checked=False, fn=callback: fn())
            return button

        def _apply_theme(self, theme_key=None):
            self.theme_key = set_active_theme(theme_key or self.theme_key)
            self.setStyleSheet(_theme_stylesheet(self.theme_key))
            if getattr(self, "theme_badge", None) is not None:
                self.theme_badge.setText("Theme  {0}".format(_theme_label(self.theme_key)))
            if getattr(self, "theme_button", None) is not None:
                self.theme_button.setText(_theme_toggle_caption(self.theme_key))
                self.theme_button.setToolTip(_theme_tooltip(self.theme_key))
            _style_donate_button(getattr(self, "donate_button", None), self.theme_key)
            _apply_app_theme(self.theme_key)

        def _toggle_theme(self):
            self._apply_theme(_other_theme(self.theme_key))
            _append_status("Theme switched to {0}.".format(_theme_label(self.theme_key)))
            _refresh_dashboard()

        def _cleaner_base_name(self):
            return set_prop_marker_base_name(getattr(self, "prop_marker_base_field", None).text() if getattr(self, "prop_marker_base_field", None) is not None else get_prop_marker_base_name())

        def _run_scene_cleaner(self):
            _on_clean_scene(prop_marker_base_name=self._cleaner_base_name())

        def _run_marker_cleanup(self):
            _on_clean_markers(prop_marker_base_name=self._cleaner_base_name())

        def _open_follow_url(self, url=None):
            if _open_external_url(url or FOLLOW_AMIR_URL):
                _append_status("Opened followamir.com.")
                _refresh_dashboard()
            else:
                _append_status("Could not open followamir.com from this MotionBuilder session.")
                _refresh_dashboard()

        def _open_donate_url(self):
            if DONATE_URL and _open_external_url(DONATE_URL):
                _append_status("Opened the Donate link.")
                _refresh_dashboard()
            else:
                _append_status("Could not open the Donate link from this MotionBuilder session.")
                _refresh_dashboard()

    class AminateMobuDockWidget(QtWidgets.QDockWidget):
        def __init__(self, parent=None):
            super(AminateMobuDockWidget, self).__init__(TOOL_NAME, parent or _qt_host_main_window())
            self.setObjectName(QT_DOCK_OBJECT_NAME)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
            self.setFeatures(
                QtWidgets.QDockWidget.DockWidgetClosable
                | QtWidgets.QDockWidget.DockWidgetMovable
                | QtWidgets.QDockWidget.DockWidgetFloatable
            )
            self.panel = AminateMobuPanel(self)
            self.status_memo = self.panel.status_memo
            self.status_label = self.panel.status_label
            self.setWidget(self.panel)

        def closeEvent(self, event):
            global _QT_DOCK
            global _QT_TOOL
            _QT_DOCK = None
            _QT_TOOL = None
            _restore_app_theme()
            super(AminateMobuDockWidget, self).closeEvent(event)


def _populate_tool_layout(tool):
    x_pos = FBAddRegionParam(0, FBAttachType.kFBAttachLeft, "")
    y_pos = FBAddRegionParam(0, FBAttachType.kFBAttachTop, "")
    width = FBAddRegionParam(0, FBAttachType.kFBAttachRight, "")
    height = FBAddRegionParam(0, FBAttachType.kFBAttachBottom, "")
    tool.AddRegion("main", "main", x_pos, y_pos, width, height)
    container = pyfbsdk_additions.FBVBoxLayout(FBAttachType.kFBAttachTop)
    tool.SetControl("main", container)

    title = FBLabel()
    title.Caption = TOOL_NAME + "  " + TOOL_VERSION
    container.Add(title, 24)

    subhead = FBLabel()
    subhead.Caption = "Scene Cleaner  Auto Map  Lock Warning  Control Rig Mode Warning"
    container.Add(subhead, 20)

    row = pyfbsdk_additions.FBHBoxLayout(FBAttachType.kFBAttachLeft)
    row.Add(_button("Refresh", _on_refresh, color=(0.18, 0.36, 0.64)), 96)
    row.Add(_button("Scene Cleaner", _on_clean_scene, color=(0.10, 0.44, 0.40)), 120)
    row.Add(_button("Delete Cameras", _on_clean_cameras, color=(0.16, 0.26, 0.42)), 120)
    row.Add(_button("Delete Markers", _on_clean_markers, color=(0.16, 0.26, 0.42)), 120)
    container.Add(row, 28)

    row = pyfbsdk_additions.FBHBoxLayout(FBAttachType.kFBAttachLeft)
    row.Add(_button("Auto Map Skeleton", _on_auto_map, color=(0.40, 0.24, 0.10)), 150)
    row.Add(_button("Validate Character", _on_validate, color=(0.26, 0.24, 0.40)), 150)
    row.Add(_button("Body Part Mode", _on_body_part, color=(0.24, 0.34, 0.14)), 130)
    row.Add(_button("Full Body Mode", _on_full_body, color=(0.24, 0.34, 0.14)), 130)
    container.Add(row, 28)

    row = pyfbsdk_additions.FBHBoxLayout(FBAttachType.kFBAttachLeft)
    row.Add(_button("History Timeline", _on_history_timeline, color=(0.46, 0.34, 0.12)), 180)
    container.Add(row, 28)

    note = FBEdit()
    note.ReadOnly = True
    note.Text = SCENE_CLEANER_HINT
    container.Add(note, 36)

    memo = FBMemo()
    tool.status_memo = memo
    container.AddRelative(memo, 1.0)


def launch_aminate_mobu():
    global _QT_TOOL
    global _QT_DOCK
    global _TOOL
    install_runtime_watchers()
    _ensure_aminate_launcher_toolbar()
    if QtWidgets is not None and hasattr(_qt_host_main_window(), "addDockWidget"):
        if _QT_DOCK is None:
            existing_docks = _existing_aminate_mobu_docks()
            if existing_docks:
                _QT_DOCK = existing_docks[-1]
                _close_duplicate_aminate_mobu_docks(keep_dock=_QT_DOCK)
                _QT_TOOL = getattr(_QT_DOCK, "panel", None)
        if _QT_DOCK is None:
            main = _qt_host_main_window()
            _QT_DOCK = AminateMobuDockWidget(parent=main)
            _QT_TOOL = _QT_DOCK.panel
            try:
                main.addDockWidget(QtCore.Qt.RightDockWidgetArea, _QT_DOCK)
            except Exception:
                pass
            _close_duplicate_aminate_mobu_docks(keep_dock=_QT_DOCK)
        try:
            _QT_DOCK.show()
            _QT_DOCK.raise_()
        except Exception:
            pass
        _set_status_lines(_tool_intro_lines())
        _refresh_dashboard()
        return _QT_DOCK
    if TOOL_NAME in pyfbsdk_additions.FBToolList:
        _TOOL = pyfbsdk_additions.FBToolList[TOOL_NAME]
        try:
            _TOOL.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosLeft)
            _TOOL.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosRight)
            _TOOL.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosTop)
            _TOOL.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosBottom)
        except Exception:
            pass
        ShowTool(_TOOL)
        _refresh_dashboard()
        return _TOOL
    tool = pyfbsdk_additions.FBCreateUniqueTool(TOOL_NAME)
    tool.StartSizeX = 760
    tool.StartSizeY = 420
    try:
        tool.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosLeft)
        tool.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosRight)
        tool.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosTop)
        tool.SetPossibleDockPosition(FBToolPossibleDockPosition.kFBToolPossibleDockPosBottom)
    except Exception:
        pass
    _populate_tool_layout(tool)
    ShowTool(tool)
    _TOOL = tool
    _set_status_lines(_tool_intro_lines())
    _refresh_dashboard()
    return tool


__all__ = [
    "CONTROL_RIG_MODE_WARNING",
    "LOCK_DEFINITION_WARNING",
    "SCENE_CLEANER_HINT",
    "TOOL_NAME",
    "TOOL_VERSION",
    "auto_map_character",
    "character_setup_seems_done",
    "collect_scene_clean_targets",
    "get_prop_marker_base_name",
    "get_warning_history",
    "handle_transform_attempt",
    "install_motionbuilder_startup",
    "install_runtime_watchers",
    "launch_aminate_mobu",
    "maybe_warn_control_rig_mode",
    "maybe_warn_lock_definition",
    "remove_runtime_watchers",
    "reset_runtime_state",
    "run_scene_cleaner",
    "set_prop_marker_base_name",
    "set_keying_mode_body_part",
    "set_keying_mode_full_body",
    "startup_bootstrap_path",
    "ensure_motionbuilder_ui_entry",
    "validate_current_character",
]
