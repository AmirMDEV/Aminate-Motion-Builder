"""
Aminate Mobu

MotionBuilder sibling toolkit for Aminate.
"""

from __future__ import annotations

import base64
import json
import math
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
    FBModelTransformationType,
    FBPlayerControl,
    FBPopup,
    ShowTool,
    FBStringList,
    FBSystem,
    FBTime,
    FBTimeReferential,
    FBTextJustify,
    FBToolPossibleDockPosition,
    FBVector3d,
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
LAUNCHER_ICON_RELATIVE_PATH = os.path.join("assets", "icons", "aminate_toolbar_18.png")
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
EASY_TOOLTIP_TEXT = {
    "Aminate": "Open Aminate Mobu tools.",
    "File": "Open files, save work, import, export, and close the scene.",
    "Edit": "Undo, redo, copy, paste, and other basic scene edits.",
    "Animation": "Work with keys, takes, layers, plotting, and animation tools.",
    "Settings": "Change MotionBuilder preferences and scene options.",
    "Layout": "Show, hide, and reset panel layouts.",
    "Open Reality": "Open live device, camera, and realtime connection tools.",
    "Python Tools": "Open MotionBuilder scripting and Python helper tools.",
    "Window": "Show, hide, and arrange MotionBuilder windows.",
    "Help": "Open help, docs, and version information.",
    "Viewer": "This is the main 3D view where you look at and work in the scene.",
    "View": "Choose which camera or view the Viewer uses.",
    "Display": "Choose what the Viewer draws, like grids, helpers, and models.",
    "Renderer": "Choose how the Viewer draws the scene.",
    "Transport Controls": "Play, stop, scrub, and move through time.",
    "Story": "Build clip based timing and non linear animation.",
    "Action": "Work with action clips and their timing.",
    "Navigator": "Browse everything in the scene.",
    "Dopesheet": "See and move keys in a simple timeline view.",
    "FCurves": "Edit animation curves and smooth motion.",
    "Key Controls": "Change how keys are created, moved, flattened, and synced.",
    "Resources": "Browse assets, scripts, templates, and scene resources.",
    "Character Controls": "Create, define, characterize, and drive characters.",
    "Create": "Make a new actor or control rig.",
    "Actor": "Create an actor setup for device or optical data.",
    "Control Rig": "Build an animatable rig with controls.",
    "Define": "Connect skeleton parts to a character definition.",
    "Skeleton": "Map skeleton bones into the character system.",
    "Actions": "Main Aminate tools for cleaning, mapping, and setup checks.",
    "Notes": "Simple rules and reminders for how Aminate behaves.",
    "What This Tool Helps With": "Quick summary of what Aminate Mobu can do for this scene.",
    "Prop Marker Base Name": "Type the base name Aminate should use when renaming animated prop markers.",
    "Refresh": "Re-read the current scene and refresh Aminate status.",
    "Scene Cleaner": "Delete user cameras, remove junk default markers, and keep animated prop markers.",
    "Delete Cameras": "Delete user made cameras from the scene.",
    "Delete Markers": "Delete junk default markers and keep animated prop markers.",
    "Auto Map Skeleton": "Try to map the current skeleton into HumanIK from hips to fingers and feet.",
    "T-Pose Frame 1": "Put the current character into MotionBuilder stance T-pose on frame 1 and key it there only.",
    "Validate Character": "Check whether the character setup is ready and warn about missing steps.",
    "Body Part Mode": "Switch the control rig into body part editing mode.",
    "Full Body Mode": "Switch the control rig into full body editing mode.",
    "History Timeline": "Open the History Timeline tool for full scene snapshot branches.",
    "Definition Manager": "Save and reload character definition presets.",
    "Refresh Definitions": "Reload the saved definition preset list.",
    "Save Definition": "Save the current character definition links as a reusable preset.",
    "Load Definition": "Load the selected definition preset onto the current character.",
    "Rename Definition": "Rename the selected definition preset using the name field.",
    "Delete Definition": "Delete the selected saved definition preset.",
    "Donate": "Open Amir's PayPal donation page.",
    "Theme": "Shows which Aminate theme is active right now.",
    "Ready.": "This line shows the latest Aminate status message.",
}
AMINATE_MOBU_LOCAL_STYLESHEETS = {
THEME_MOTIONBUILDER: "",
THEME_MODERN: """
QWidget#aminateMobuWindow {
    background-color: #2F363E;
    color: #D8DEE5;
}
QWidget#aminateMobuWindow QLabel {
    font-size: 10px;
}
QLabel#aminateMobuHeaderTitle {
    color: #F2F5F8;
    font-size: 13px;
    font-weight: 600;
}
QLabel#aminateMobuHeaderSubtitle {
    color: #99A5B0;
    font-size: 9px;
}
QLabel#aminateMobuThemeBadge {
    background-color: #283038;
    color: #C7D1DB;
    border: 1px solid #43515E;
    border-radius: 3px;
    font-size: 9px;
    padding: 3px 8px;
}
QFrame#mayaAnimWorkflowTabIntro {
    background-color: #313A43;
    color: #DFE5EA;
    border: 1px solid #45525E;
    border-left: 3px solid #6D879A;
    border-radius: 4px;
}
QLabel#mayaAnimWorkflowIntroTitle {
    color: #F1F4F7;
    font-size: 11px;
    font-weight: 700;
}
QLabel#mayaAnimWorkflowIntroBody {
    color: #C5CED7;
    font-size: 10px;
}
QLabel#mayaAnimWorkflowStatusLabel {
    background-color: #252C33;
    color: #E1E6EB;
    border: 1px solid #3E4A55;
    border-radius: 4px;
    font-size: 10px;
    padding: 4px 7px;
}
QPlainTextEdit#aminateMobuStatusMemo {
    background-color: #21272E;
    color: #D8DEE4;
    border: 1px solid #404C57;
    border-radius: 3px;
    font-size: 10px;
    padding: 5px;
    selection-background-color: #526A7F;
}
QLabel#mayaAnimWorkflowBrandLabel,
QLabel#mayaAnimWorkflowVersionLabel,
QLabel#aminateMobuGroupHint {
    color: #8D99A4;
    font-size: 9px;
}
QPushButton#aminateMobuThemeToggle {
    background-color: #38424C;
    border: 1px solid #546372;
    border-radius: 4px;
    padding: 4px 12px;
    color: #EDF1F4;
    font-weight: 600;
    outline: none;
}
QPushButton#aminateMobuThemeToggle:hover {
    background-color: #45505C;
    border-color: #6D7E8F;
}
QPushButton#aminateMobuThemeToggle:pressed {
    background-color: #2E3740;
    border-color: #73889C;
}
QPushButton,
QToolButton,
QAbstractButton {
    background-color: #3A434D;
    color: #E9EDF1;
    border: 1px solid #53616F;
    border-radius: 4px;
    padding: 4px 10px;
    font-weight: 600;
    outline: none;
}
QPushButton:hover,
QToolButton:hover,
QAbstractButton:hover {
    background-color: #45505C;
    border-color: #687A8C;
}
QPushButton:pressed,
QToolButton:pressed,
QAbstractButton:pressed {
    background-color: #2F3740;
    border-color: #73879B;
}
QPushButton:checked,
QToolButton:checked,
QAbstractButton:checked {
    background-color: #516374;
    border-color: #7E96AA;
}
QPushButton:disabled,
QToolButton:disabled,
QAbstractButton:disabled {
    background-color: #262C32;
    color: #74808A;
    border-color: #3D4852;
}
QLineEdit,
QPlainTextEdit,
QTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: #252C33;
    color: #DEE4EA;
    border: 1px solid #43505C;
    border-radius: 3px;
    padding: 3px 6px;
    selection-background-color: #526A7F;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #45515D;
    background-color: #2D353E;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}
QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-color: #6F889E;
}
QCheckBox,
QRadioButton,
QLabel {
    color: #D8DEE5;
}
QGroupBox {
    background-color: #313943;
    color: #E3E8ED;
    border: 1px solid #44515D;
    border-radius: 5px;
    margin-top: 10px;
    padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    font-size: 10px;
    padding: 0px 5px;
    color: #E9EEF2;
    background-color: #38434F;
    border: 1px solid #546271;
    border-radius: 3px;
}
QTabWidget::pane {
    border: 1px solid #44515D;
    border-radius: 6px;
    top: -1px;
    background-color: #29313A;
    padding: 2px;
}
QTabBar::tab {
    background-color: #313A43;
    color: #B8C4CF;
    border: 1px solid #465462;
    border-bottom: 0px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 4px 10px;
    margin-right: 2px;
    min-width: 38px;
}
QTabBar::tab:hover {
    background-color: #39434D;
    color: #ECF1F5;
    border-color: #58697A;
}
QTabBar::tab:selected {
    background-color: #405262;
    color: #F3F6F8;
    border-color: #6F889D;
    padding-bottom: 5px;
}
QTabBar::tab:!selected {
    margin-top: 2px;
}
QSplitter::handle:horizontal {
    width: 2px;
    background-color: #46525D;
}
QSplitter::handle:vertical {
    height: 2px;
    background-color: #46525D;
}
QScrollBar:vertical,
QScrollBar:horizontal {
    background-color: #232A31;
    border: 0px;
    margin: 0px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background-color: #46515D;
    border-radius: 4px;
    min-height: 18px;
    min-width: 18px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background-color: #55616D;
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
    color: #D6DDE4;
    background-color: #29313A;
    selection-background-color: #4D677E;
    selection-color: #F2F5F8;
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
    background-color: #273039;
}
QDockWidget > QWidget,
QStackedWidget > QWidget,
QTabWidget > QWidget,
QDockWidget QWidget,
QStackedWidget QWidget,
QTabWidget QWidget,
QAbstractScrollArea > QWidget,
QAbstractScrollArea > QWidget > QWidget,
QFrame {
    background-color: #242D35;
}
QDockWidget QLabel,
QStackedWidget QLabel,
QTabWidget QLabel {
    background-color: transparent;
}
QDockWidget::title {
    background-color: #2D3741;
    color: #DEE4EA;
    padding-left: 10px;
    padding-right: 34px;
    padding-top: 4px;
    padding-bottom: 4px;
    border-bottom: 1px solid #43515D;
}
QDockWidget {
    border: 1px solid #42505B;
}
QDockWidget::close-button,
QDockWidget::float-button {
    background-color: #3A434D;
    border: 1px solid #52606E;
    border-radius: 4px;
    padding: 1px;
}
QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background-color: #46515D;
    border-color: #687A8C;
}
QDockWidget::close-button:pressed,
QDockWidget::float-button:pressed {
    background-color: #2F3740;
    border-color: #73879B;
}
QMenuBar {
    border-bottom: 1px solid #3F4C58;
    background-color: #25303A;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    margin: 1px 2px;
    color: #D8DEE5;
    border-radius: 4px;
}
QMenuBar::item:selected,
QMenu::item:selected {
    background-color: #37414C;
    color: #F0F3F6;
}
QMenuBar::item:pressed {
    background-color: #313A43;
    color: #F4F6F8;
}
QMenu {
    background-color: #2A3138;
    border: 1px solid #42505B;
}
QMenu::item {
    padding: 6px 22px;
}
QMenu::separator {
    height: 1px;
    background-color: #43515E;
    margin: 4px 10px;
}
QToolBar {
    border: 0px;
    spacing: 3px;
    background-color: #2C3640;
}
QToolBar::separator {
    background-color: #44525F;
    width: 1px;
    margin: 4px 4px;
}
QToolButton#aminateMobuLauncherButton {
    background-color: #34404B;
    border: 1px solid #607589;
    border-radius: 5px;
    color: #EDF2F5;
    padding: 4px 10px;
    font-weight: 600;
}
QToolButton#aminateMobuLauncherButton:hover {
    background-color: #3F4C59;
    border: 1px solid #7890A5;
}
QToolButton#aminateMobuLauncherButton:pressed,
QToolButton#aminateMobuLauncherButton:checked {
    background-color: #2C3540;
    border: 1px solid #8099AF;
}
QPushButton,
QToolButton,
QAbstractButton {
    background-color: #39434D;
    color: #E9EEF2;
    border: 1px solid #52616F;
    border-radius: 5px;
    padding: 4px 10px;
    font-weight: 600;
}
QComboBox,
QAbstractSpinBox,
QLineEdit,
QPlainTextEdit,
QTextEdit {
    background-color: #242B32;
    color: #E6EBEF;
    border: 1px solid #42505B;
    border-radius: 4px;
    padding: 4px 8px;
}
QToolBar QToolButton,
QToolBar QAbstractButton,
QToolBar QComboBox,
QToolBar QAbstractSpinBox {
    background-color: #36404A;
    border: 1px solid #4E5D6C;
    border-radius: 4px;
    padding: 2px 7px;
}
QToolBar QToolButton:hover,
QToolBar QAbstractButton:hover,
QToolBar QComboBox:hover,
QToolBar QAbstractSpinBox:hover {
    background-color: #414C58;
    border-color: #65788A;
}
QToolBar QToolButton:pressed,
QToolBar QAbstractButton:pressed,
QToolBar QToolButton:checked {
    background-color: #2E3741;
    border-color: #73879C;
}
QToolBar QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 14px;
    border-left: 1px solid #4C5A67;
    background-color: #2D353E;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QToolBar QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #465461;
    background-color: #2D353E;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}
QComboBox QAbstractItemView {
    background-color: #252C33;
    color: #E7ECF0;
    border: 1px solid #45515D;
    selection-background-color: #4F667B;
    selection-color: #F4F7F9;
    outline: 0px;
}
QAbstractItemView {
    background-color: #252C33;
    color: #E3E8EC;
    border: 1px solid #42505D;
    outline: 0px;
}
QAbstractSpinBox::up-button,
QAbstractSpinBox::down-button {
    background-color: #2D353E;
    border-left: 1px solid #465461;
    width: 15px;
}
QAbstractSpinBox::up-button:hover,
QAbstractSpinBox::down-button:hover {
    background-color: #38434E;
}
QDockWidget QLabel {
    color: #D2DAE1;
}
QDockWidget QLineEdit,
QDockWidget QComboBox,
QDockWidget QAbstractSpinBox {
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 18px;
}
QDockWidget QToolButton {
    background-color: #36404A;
    border: 1px solid #4A5A69;
    border-radius: 4px;
    padding: 1px 5px;
    min-height: 17px;
    font-weight: 500;
}
QDockWidget QAbstractButton {
    background-color: #36404A;
    color: #DDE4EA;
    border: 1px solid #4A5A69;
    border-radius: 4px;
    padding: 1px 5px;
}
QDockWidget QToolButton:hover,
QDockWidget QAbstractButton:hover,
QDockWidget QComboBox:hover,
QDockWidget QAbstractSpinBox:hover,
QDockWidget QLineEdit:hover {
    border-color: #708498;
}
QDockWidget QComboBox::drop-down {
    width: 13px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QDockWidget QAbstractSpinBox::up-button,
QDockWidget QAbstractSpinBox::down-button {
    width: 13px;
}
QDockWidget QComboBox QAbstractItemView::item {
    padding: 3px 8px;
    min-height: 18px;
}
QPushButton:hover,
QToolButton:hover,
QAbstractButton:hover {
    background-color: #44505C;
    border-color: #697C8E;
}
QComboBox:hover,
QAbstractSpinBox:hover,
QLineEdit:hover,
QPlainTextEdit:hover,
QTextEdit:hover {
    border-color: #697C8E;
}
QPushButton:pressed,
QToolButton:pressed,
QAbstractButton:pressed {
    background-color: #2F3740;
    border-color: #73879B;
}
QPushButton:checked,
QToolButton:checked,
QAbstractButton:checked,
QToolButton:selected {
    background-color: #516374;
    border-color: #8098AC;
}
QPushButton:disabled,
QToolButton:disabled,
QAbstractButton:disabled,
QComboBox:disabled,
QAbstractSpinBox:disabled {
    background-color: #262C32;
    color: #77818A;
    border-color: #3D4852;
}
QLineEdit:focus,
QPlainTextEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QAbstractSpinBox:focus {
    border: 1px solid #6F889E;
}
QHeaderView::section {
    background-color: #2D3741;
    color: #DEE5EB;
    border: 1px solid #43515E;
    padding: 4px 8px;
    font-weight: 600;
}
QTabWidget::pane {
    border: 1px solid #42505C;
    border-radius: 6px;
    top: -1px;
    background-color: #242D35;
    padding: 2px;
}
QTabBar::tab {
    background-color: #313A43;
    color: #BBC6D0;
    border: 1px solid #465361;
    border-bottom: 0px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 4px 11px;
    margin-right: 3px;
    min-width: 40px;
}
QTabBar::tab:hover {
    background-color: #39434D;
    color: #EEF2F5;
    border-color: #566879;
}
QTabBar::tab:selected {
    background-color: #415264;
    color: #F4F7F9;
    border-color: #70899E;
    padding-bottom: 5px;
}
QTabBar::tab:!selected {
    margin-top: 2px;
}
QTreeView,
QListView,
QTableView {
    background-color: #1F262D;
    alternate-background-color: #273039;
    gridline-color: #43515E;
    border: 1px solid #42505D;
    show-decoration-selected: 1;
}
QTreeView::item,
QListView::item,
QTableView::item {
    padding-top: 2px;
    padding-bottom: 2px;
    padding-left: 5px;
    padding-right: 5px;
    border: 1px solid transparent;
}
QTreeView::item:selected,
QListView::item:selected,
QTableView::item:selected {
    background-color: #4F667B;
    color: #F4F7F9;
    border-color: #748EA4;
}
QTreeView::item:hover,
QListView::item:hover,
QTableView::item:hover {
    background-color: #333D47;
}
QSplitter::handle:horizontal {
    width: 2px;
    background-color: #43505C;
}
QSplitter::handle:vertical {
    height: 2px;
    background-color: #43505C;
}
QScrollBar:vertical,
QScrollBar:horizontal {
    background: #21282F;
    border: 0px;
    margin: 0px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #44505C;
    border-radius: 4px;
    min-height: 18px;
    min-width: 18px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover {
    background: #56626E;
}
QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}
QStatusBar {
    border-top: 1px solid #3F4C58;
}
QStatusBar::item {
    border: 0px;
}
QStatusBar QLabel {
    color: #CDD5DD;
    padding-left: 1px;
    padding-right: 2px;
}
QGroupBox {
    border: 1px solid #44525E;
    border-radius: 6px;
    margin-top: 10px;
    padding: 10px;
    background-color: #28313A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 1px 6px;
    color: #E8EEF3;
    background-color: #38444F;
    border: 1px solid #526171;
    border-radius: 4px;
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
_QT_TOOLTIP_FILTER = None
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
APP_BASELINE_STYLESHEET_ATTR = "_aminate_mobu_baseline_stylesheet"
APP_BASELINE_PALETTE_ATTR = "_aminate_mobu_baseline_palette"
APP_BASELINE_STYLE_ATTR = "_aminate_mobu_baseline_style"
DEFAULT_UI_SNAPSHOT_FILENAME = "motionbuilder_default_ui_snapshot.json"


def _now():
    return time.time()


def _safe_caption(text):
    return str(text or "").strip()


def _module_root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _user_data_dir():
    path = os.path.join(os.path.expanduser("~"), "Documents", "MB", "AminateMobu")
    os.makedirs(path, exist_ok=True)
    return path


def _definition_store_path():
    return os.path.join(_user_data_dir(), "character_definitions.json")


def _default_ui_snapshot_path():
    return os.path.join(_module_root_dir(), DEFAULT_UI_SNAPSHOT_FILENAME)


def _byte_array_to_base64(value):
    if value is None:
        return ""
    try:
        return bytes(value.toBase64()).decode("ascii")
    except Exception:
        try:
            return base64.b64encode(bytes(value)).decode("ascii")
        except Exception:
            return ""


def _byte_array_from_base64(text):
    if not text or QtCore is None:
        return None
    try:
        return QtCore.QByteArray.fromBase64(text.encode("ascii"))
    except Exception:
        try:
            data = base64.b64decode(text.encode("ascii"))
            payload = QtCore.QByteArray()
            payload.append(data)
            return payload
        except Exception:
            return None


def capture_current_ui_snapshot(main=None, snapshot_path=None):
    main = main or _qt_host_main_window()
    if main is None:
        return None
    if not hasattr(main, "saveState") or not hasattr(main, "saveGeometry"):
        return None
    app = _qt_application()
    theme_key = get_active_theme()
    snapshot = {
        "version": 1,
        "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "theme_key_at_capture": theme_key,
        "window_title": _safe_caption(getattr(main, "windowTitle", lambda: "")()),
        "app_stylesheet_length": len((app.styleSheet() or "")) if app is not None else 0,
        "layout_only": True,
        "geometry_b64": _byte_array_to_base64(main.saveGeometry()),
        "state_b64": _byte_array_to_base64(main.saveState()),
    }
    snapshot_path = snapshot_path or _default_ui_snapshot_path()
    with open(snapshot_path, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
    return snapshot_path


def ensure_default_ui_snapshot(main=None, force=False):
    snapshot_path = _default_ui_snapshot_path()
    if not force and os.path.isfile(snapshot_path):
        return snapshot_path
    return capture_current_ui_snapshot(main=main, snapshot_path=snapshot_path)


def _restore_saved_ui_snapshot(main=None, snapshot_path=None):
    main = main or _qt_host_main_window()
    if main is None:
        return False
    snapshot_path = snapshot_path or _default_ui_snapshot_path()
    if not os.path.isfile(snapshot_path):
        return False
    try:
        with open(snapshot_path, "r", encoding="utf-8") as handle:
            snapshot = json.load(handle)
    except Exception:
        return False
    restored = False
    geometry = _byte_array_from_base64(snapshot.get("geometry_b64", ""))
    state = _byte_array_from_base64(snapshot.get("state_b64", ""))
    try:
        if geometry is not None and not geometry.isEmpty() and hasattr(main, "restoreGeometry"):
            restored = bool(main.restoreGeometry(geometry)) or restored
    except Exception:
        pass
    try:
        if state is not None and not state.isEmpty() and hasattr(main, "restoreState"):
            restored = bool(main.restoreState(state)) or restored
    except Exception:
        pass
    return restored


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


def _name_tokens(name):
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(name or ""))
    tokens = [item.lower() for item in re.split(r"[^A-Za-z0-9]+", text) if item]
    return [item for item in tokens if item not in ("mixamorig", "bip", "bone", "joint", "skel", "jnt")]


def _side_from_tokens(tokens, normalized):
    token_set = set(tokens)
    if token_set.intersection(("left", "l")) or normalized.startswith("left") or normalized.endswith("left"):
        return "left"
    if token_set.intersection(("right", "r")) or normalized.startswith("right") or normalized.endswith("right"):
        return "right"
    return ""


def _slot_side(slot_name):
    if slot_name.startswith("Left"):
        return "left"
    if slot_name.startswith("Right"):
        return "right"
    return ""


def _slot_number(slot_name):
    match = re.search(r"(\d+)Link$", slot_name)
    return int(match.group(1)) if match else None


def _token_has_number(tokens, number):
    if number is None:
        return True
    wanted = str(number)
    padded = "0{0}".format(number)
    return any(item == wanted or item == padded or item.endswith(wanted) for item in tokens)


def _auto_map_slot_terms(slot_name):
    base = slot_name.replace("Left", "").replace("Right", "")
    base = re.sub(r"\d+Link$", "Link", base)
    terms = {
        "ReferenceLink": ("reference", "root"),
        "HipsLink": ("hips", "hip", "pelvis"),
        "HipsTranslationLink": ("hips", "hip", "pelvis"),
        "SpineLink": ("spine", "waist"),
        "NeckLink": ("neck",),
        "HeadLink": ("head",),
        "ShoulderLink": ("shoulder", "clavicle", "collar"),
        "ArmLink": ("upperarm", "uparm", "arm"),
        "ArmRollLink": ("upperarmtwist", "upperarmroll", "uparmtwist", "twist"),
        "ForeArmLink": ("lowerarm", "forearm", "loarm"),
        "ForeArmRollLink": ("lowerarmtwist", "forearmtwist", "lowerarmroll", "twist"),
        "HandLink": ("hand", "wrist"),
        "UpLegLink": ("upleg", "upperleg", "thigh"),
        "UpLegRollLink": ("thightwist", "uplegtwist", "upperlegtwist", "thighroll", "twist"),
        "LegLink": ("leg", "lowerleg", "calf", "shin"),
        "LegRollLink": ("calftwist", "legtwist", "lowerlegtwist", "calfroll", "twist"),
        "FootLink": ("foot", "ankle"),
        "ToeBaseLink": ("toebase", "toe", "ball"),
        "HandThumbLink": ("thumb",),
        "HandIndexLink": ("index", "pointer"),
        "HandMiddleLink": ("middle",),
        "HandRingLink": ("ring",),
        "HandPinkyLink": ("pinky", "little"),
    }
    if "Thumb" in slot_name:
        return terms["HandThumbLink"]
    if "Index" in slot_name:
        return terms["HandIndexLink"]
    if "Middle" in slot_name:
        return terms["HandMiddleLink"]
    if "Ring" in slot_name:
        return terms["HandRingLink"]
    if "Pinky" in slot_name:
        return terms["HandPinkyLink"]
    return terms.get(base, ())


def _candidate_slot_score(slot_name, normalized_name, model):
    short_name = _short_name_from_long_name(_component_long_name(model))
    tokens = _name_tokens(short_name)
    token_set = set(tokens)
    side = _slot_side(slot_name)
    if side and _side_from_tokens(tokens, normalized_name) != side:
        return 0
    if not side and _side_from_tokens(tokens, normalized_name):
        return 0

    score = 0
    for candidate in CHARACTER_SLOT_CANDIDATES.get(slot_name, ()):
        candidate_norm = _normalize_name(candidate)
        if normalized_name == candidate_norm:
            score = max(score, 100)
        elif normalized_name.endswith(candidate_norm) or normalized_name.startswith(candidate_norm):
            score = max(score, 75)

    terms = _auto_map_slot_terms(slot_name)
    compact_tokens = {_normalize_name(item) for item in tokens}
    for term in terms:
        term_norm = _normalize_name(term)
        if term_norm in compact_tokens:
            score = max(score, 70 if len(term_norm) > 5 else 60)
        elif term_norm in normalized_name:
            score = max(score, 85 if len(term_norm) > 5 else 60)

    if score <= 0:
        return 0

    number = _slot_number(slot_name)
    finger_slot = any(name in slot_name for name in ("Thumb", "Index", "Middle", "Ring", "Pinky"))
    if finger_slot and not _token_has_number(tokens, number):
        return 0
    if finger_slot and "metacarpal" in token_set:
        score -= 20
    if "RollLink" in slot_name and not ("twist" in normalized_name or "roll" in normalized_name):
        return 0
    if "RollLink" not in slot_name and ("twist" in normalized_name or "roll" in normalized_name):
        score -= 25
    if "ToeBaseLink" in slot_name and "ik" in token_set:
        return 0
    if slot_name in ("ReferenceLink", "HipsLink", "HipsTranslationLink") and "ik" in token_set:
        return 0
    if "Spine" in slot_name:
        number = _slot_number(slot_name)
        if number is None:
            if any(item in token_set for item in ("01", "1")):
                score += 15
        elif _token_has_number(tokens, number):
            score += 15
        else:
            score -= 25
    if "RollLink" in slot_name:
        if any(item in token_set for item in ("01", "1")):
            score += 8
        if any(item in token_set for item in ("02", "2")):
            score -= 2
    if side:
        score += 10
    return score


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


def _theme_string_is_modern(stylesheet):
    return (stylesheet or "").strip() == _app_theme_stylesheet(THEME_MODERN).strip()


def _sync_baseline_from_app_cache(app=None):
    global _APP_THEME_BASELINE, _APP_THEME_BASELINE_PALETTE, _APP_THEME_BASELINE_STYLE
    app = app or _qt_application()
    if app is None:
        return False
    changed = False
    try:
        cached_stylesheet = getattr(app, APP_BASELINE_STYLESHEET_ATTR, None)
        if cached_stylesheet is not None and _APP_THEME_BASELINE is None:
            _APP_THEME_BASELINE = cached_stylesheet
            changed = True
    except Exception:
        pass
    try:
        cached_palette = getattr(app, APP_BASELINE_PALETTE_ATTR, None)
        if cached_palette is not None and _APP_THEME_BASELINE_PALETTE is None:
            _APP_THEME_BASELINE_PALETTE = _copy_palette(cached_palette)
            changed = True
    except Exception:
        pass
    try:
        cached_style = getattr(app, APP_BASELINE_STYLE_ATTR, None)
        if cached_style is not None and _APP_THEME_BASELINE_STYLE is None:
            _APP_THEME_BASELINE_STYLE = cached_style
            changed = True
    except Exception:
        pass
    return changed


def _store_baseline_on_app(app=None):
    app = app or _qt_application()
    if app is None:
        return False
    try:
        setattr(app, APP_BASELINE_STYLESHEET_ATTR, _APP_THEME_BASELINE)
    except Exception:
        pass
    try:
        setattr(app, APP_BASELINE_PALETTE_ATTR, _copy_palette(_APP_THEME_BASELINE_PALETTE))
    except Exception:
        pass
    try:
        setattr(app, APP_BASELINE_STYLE_ATTR, _APP_THEME_BASELINE_STYLE)
    except Exception:
        pass
    return True


def _reset_to_best_effort_native(app):
    if app is None:
        return False
    try:
        app.setStyleSheet("")
    except Exception:
        pass
    style_applied = False
    if QtWidgets is not None and hasattr(QtWidgets, "QStyleFactory"):
        try:
            keys = [str(key) for key in QtWidgets.QStyleFactory.keys()]
        except Exception:
            keys = []
        preferred = None
        for wanted in ("WindowsVista", "Windows11", "Windows", "Fusion"):
            for key in keys:
                if key.lower() == wanted.lower():
                    preferred = key
                    break
            if preferred:
                break
        if preferred:
            try:
                app.setStyle(preferred)
                style_applied = True
            except Exception:
                style_applied = False
    try:
        style = app.style()
        if style is not None:
            app.setPalette(style.standardPalette())
    except Exception:
        pass
    return style_applied


def prime_app_theme_baseline(force_reset=False):
    global _APP_THEME_BASELINE, _APP_THEME_BASELINE_PALETTE, _APP_THEME_BASELINE_STYLE
    app = _qt_application()
    if app is None:
        return False
    _sync_baseline_from_app_cache(app)
    if not force_reset and _APP_THEME_BASELINE is not None and _APP_THEME_BASELINE_PALETTE is not None:
        return True
    current_stylesheet = app.styleSheet() or ""
    if force_reset or _theme_string_is_modern(current_stylesheet):
        _reset_to_best_effort_native(app)
        current_stylesheet = app.styleSheet() or ""
    _APP_THEME_BASELINE = current_stylesheet
    _APP_THEME_BASELINE_PALETTE = _copy_palette(app.palette())
    try:
        _APP_THEME_BASELINE_STYLE = app.style().objectName()
    except Exception:
        _APP_THEME_BASELINE_STYLE = None
    _store_baseline_on_app(app)
    return True


def _clean_tooltip_key(text):
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", str(text).replace("&", " ")).strip()
    while cleaned.endswith(":"):
        cleaned = cleaned[:-1].rstrip()
    return cleaned


def _easy_tooltip_text(text, class_name=""):
    key = _clean_tooltip_key(text)
    if not key:
        return None
    if key in EASY_TOOLTIP_TEXT:
        return EASY_TOOLTIP_TEXT[key]
    lower_key = key.lower()
    if re.match(r"take\s+\d+", lower_key):
        return "This is the active take, which stores one version of your animation."
    if re.match(r"animlayer\d+", key):
        return "This animation layer stores one stack of keys on top of the base animation."
    if lower_key == "none":
        return "Nothing is set here yet."
    if "version" in lower_key and "beta" in lower_key:
        return "This shows which Aminate Mobu build is loaded."
    if class_name == "QPushButton":
        return "Click to use {0}.".format(lower_key)
    if class_name == "QToolButton":
        return "Click to open or use {0}.".format(lower_key)
    if class_name == "QAction":
        return "Open {0} options.".format(lower_key)
    if class_name == "QMenu":
        return "Open the {0} menu.".format(lower_key)
    if class_name == "QGroupBox":
        return "This section is about {0}.".format(lower_key)
    if class_name == "QTabBar":
        return "Open the {0} tab.".format(lower_key)
    if class_name == "QLabel":
        return "This label shows {0}.".format(lower_key)
    return None


def _apply_easy_tooltip_to_action(action):
    if action is None:
        return False
    text = None
    try:
        text = action.text()
    except Exception:
        text = None
    tooltip = _easy_tooltip_text(text, "QAction")
    if not tooltip:
        return False
    changed = False
    try:
        if not action.toolTip():
            action.setToolTip(tooltip)
            changed = True
    except Exception:
        pass
    try:
        if not action.statusTip():
            action.setStatusTip(tooltip)
            changed = True
    except Exception:
        pass
    return changed


def _extract_widget_text(widget):
    for attr in ("text", "title", "windowTitle", "placeholderText"):
        try:
            value = getattr(widget, attr)()
        except Exception:
            value = None
        if value:
            return value
    try:
        value = widget.accessibleName()
    except Exception:
        value = None
    return value or ""


def _apply_easy_tooltip_to_widget(widget):
    if widget is None or QtWidgets is None:
        return False
    class_name = widget.metaObject().className() if hasattr(widget, "metaObject") else widget.__class__.__name__
    if isinstance(widget, QtWidgets.QTabBar):
        changed = False
        for index in range(widget.count()):
            tooltip = _easy_tooltip_text(widget.tabText(index), "QTabBar")
            if not tooltip:
                continue
            try:
                if not widget.tabToolTip(index):
                    widget.setTabToolTip(index, tooltip)
                    changed = True
            except Exception:
                continue
        return changed
    tooltip = _easy_tooltip_text(_extract_widget_text(widget), class_name)
    if not tooltip:
        if isinstance(widget, QtWidgets.QLineEdit):
            tooltip = "Type text here."
        elif isinstance(widget, QtWidgets.QComboBox):
            tooltip = "Choose one option from this list."
        elif isinstance(widget, QtWidgets.QPlainTextEdit):
            tooltip = "This area shows more detailed text output."
    if not tooltip:
        return False
    changed = False
    try:
        if not widget.toolTip():
            widget.setToolTip(tooltip)
            changed = True
    except Exception:
        pass
    try:
        if hasattr(widget, "setStatusTip") and not widget.statusTip():
            widget.setStatusTip(tooltip)
            changed = True
    except Exception:
        pass
    try:
        for action in widget.actions():
            _apply_easy_tooltip_to_action(action)
    except Exception:
        pass
    return changed


def refresh_easy_motionbuilder_tooltips():
    app = _qt_application()
    if QtWidgets is None or app is None:
        return 0
    touched = 0
    for widget in app.allWidgets():
        touched += int(_apply_easy_tooltip_to_widget(widget))
        try:
            for action in widget.actions():
                touched += int(_apply_easy_tooltip_to_action(action))
        except Exception:
            pass
    main = _qt_host_main_window()
    if QtGui is not None and main is not None:
        try:
            for action in main.findChildren(QtGui.QAction):
                touched += int(_apply_easy_tooltip_to_action(action))
        except Exception:
            pass
    return touched


if QtCore is not None and QtWidgets is not None:
    class MotionBuilderEasyTooltipFilter(QtCore.QObject):
        def eventFilter(self, watched, event):
            try:
                if watched is not None and event is not None:
                    if event.type() in (
                        QtCore.QEvent.Show,
                        QtCore.QEvent.Enter,
                        QtCore.QEvent.Polish,
                        QtCore.QEvent.ToolTip,
                    ):
                        if QtGui is not None and isinstance(watched, QtGui.QAction):
                            _apply_easy_tooltip_to_action(watched)
                        elif isinstance(watched, QtWidgets.QWidget):
                            _apply_easy_tooltip_to_widget(watched)
            except Exception:
                pass
            return False


def install_easy_motionbuilder_tooltips():
    global _QT_TOOLTIP_FILTER
    app = _qt_application()
    if app is None or QtCore is None or QtWidgets is None:
        return 0
    if _QT_TOOLTIP_FILTER is None:
        try:
            _QT_TOOLTIP_FILTER = MotionBuilderEasyTooltipFilter(app)
            app.installEventFilter(_QT_TOOLTIP_FILTER)
        except Exception:
            _QT_TOOLTIP_FILTER = None
    return refresh_easy_motionbuilder_tooltips()


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
        QtGui.QPalette.Window: QtGui.QColor("#25303A"),
        QtGui.QPalette.WindowText: QtGui.QColor("#DEE4EA"),
        QtGui.QPalette.Base: QtGui.QColor("#182128"),
        QtGui.QPalette.AlternateBase: QtGui.QColor("#242D35"),
        QtGui.QPalette.ToolTipBase: QtGui.QColor("#242D35"),
        QtGui.QPalette.ToolTipText: QtGui.QColor("#F0F4F7"),
        QtGui.QPalette.Text: QtGui.QColor("#E1E7EC"),
        QtGui.QPalette.Button: QtGui.QColor("#2D3741"),
        QtGui.QPalette.ButtonText: QtGui.QColor("#EDF2F5"),
        QtGui.QPalette.BrightText: QtGui.QColor("#FFFFFF"),
        QtGui.QPalette.Highlight: QtGui.QColor("#4B667E"),
        QtGui.QPalette.HighlightedText: QtGui.QColor("#F4F7F9"),
        QtGui.QPalette.Light: QtGui.QColor("#3A4957"),
        QtGui.QPalette.Midlight: QtGui.QColor("#344250"),
        QtGui.QPalette.Mid: QtGui.QColor("#2D3945"),
        QtGui.QPalette.Dark: QtGui.QColor("#141C23"),
        QtGui.QPalette.Shadow: QtGui.QColor("#10161B"),
        QtGui.QPalette.Link: QtGui.QColor("#85A7C0"),
        QtGui.QPalette.LinkVisited: QtGui.QColor("#A1B8C9"),
        QtGui.QPalette.PlaceholderText: QtGui.QColor("#7A8691"),
    }
    for role, color in colors.items():
        try:
            palette.setColor(role, color)
        except Exception:
            pass
    try:
        disabled_text = QtGui.QColor("#717D88")
        disabled_bg = QtGui.QColor("#1D252C")
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, disabled_text)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, disabled_bg)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base, disabled_bg)
        palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor("#202930"))
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
    _sync_baseline_from_app_cache(app)
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
    prime_app_theme_baseline(force_reset=theme_key == THEME_MOTIONBUILDER)
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
        _store_baseline_on_app(app)
        _refresh_qt_theme()
        _restore_saved_ui_snapshot()
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
            border-radius: 12px;
            padding: 7px 15px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #F7D46A;
        }
        QPushButton:pressed {
            background-color: #DEB03A;
        }
        """
    )


def _on_qt_panel_destroyed(*_args):
    global _QT_TOOL
    global _QT_DOCK
    _QT_TOOL = None
    _QT_DOCK = None
    _restore_app_theme()


def _launcher_icon_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, LAUNCHER_ICON_RELATIVE_PATH)
    return icon_path if os.path.isfile(icon_path) else None


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
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QtCore.QSize(18, 18))
        action = toolbar.addAction("Aminate")
        try:
            action.triggered.connect(lambda _checked=False: launch_aminate_mobu())
        except Exception:
            pass
        try:
            action.setToolTip("Open Aminate Mobu tools.")
            action.setStatusTip("Open Aminate Mobu tools.")
        except Exception:
            pass
        icon_path = _launcher_icon_path()
        if icon_path and QtGui is not None:
            try:
                action.setIcon(QtGui.QIcon(icon_path))
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
        try:
            _QT_LAUNCHER_ACTION.setToolTip("Open Aminate Mobu tools.")
            _QT_LAUNCHER_ACTION.setStatusTip("Open Aminate Mobu tools.")
        except Exception:
            pass
        icon_path = _launcher_icon_path()
        if icon_path and QtGui is not None:
            try:
                _QT_LAUNCHER_ACTION.setIcon(QtGui.QIcon(icon_path))
            except Exception:
                pass
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
    prime_app_theme_baseline()
    ensure_default_ui_snapshot()
    toolbar = _ensure_aminate_launcher_toolbar()
    install_easy_motionbuilder_tooltips()
    return toolbar


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


def _key_property_at_time(prop, time_value):
    if prop is None:
        return 0
    try:
        prop.SetAnimated(True)
    except Exception:
        pass
    try:
        prop.KeyAt(time_value)
        return 1
    except Exception:
        pass
    try:
        node = prop.GetAnimationNode()
    except Exception:
        node = None
    keyed = 0
    for child in getattr(node, "Nodes", []) or []:
        fcurve = getattr(child, "FCurve", None)
        if fcurve is None:
            try:
                child.FCurve = child.CreateFCurve()
                fcurve = child.FCurve
            except Exception:
                fcurve = None
        if fcurve is None:
            continue
        try:
            child.KeyAdd(time_value)
            keyed += 1
            continue
        except Exception:
            pass
        try:
            fcurve.KeyAdd(time_value)
            keyed += 1
        except Exception:
            pass
    return keyed


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


def _slot_match_for_index(slot_name, indexed, used_models=None):
    used_models = used_models or set()
    best_model = None
    best_score = 0
    for candidate in CHARACTER_SLOT_CANDIDATES.get(slot_name, ()):
        model = indexed.get(_normalize_name(candidate))
        if model is not None and _component_long_name(model) not in used_models:
            return model
    for normalized, model in indexed.items():
        if _component_long_name(model) in used_models:
            continue
        score = _candidate_slot_score(slot_name, normalized, model)
        if score > best_score:
            best_model = model
            best_score = score
    return best_model


def _slot_score_for_index(slot_name, indexed):
    model = _slot_match_for_index(slot_name, indexed)
    if model is None:
        return 0
    return _candidate_slot_score(slot_name, _normalize_name(_short_name_from_long_name(_component_long_name(model))), model) or 100


def _available_namespaces():
    namespaces = OrderedDict()
    for model in _scene_skeletons():
        namespaces.setdefault(_namespace_from_long_name(model.LongName), True)
    return list(namespaces.keys())


def _namespace_score(namespace):
    indexed = _index_namespace_skeletons(namespace)
    score = 0
    for slot_name in CORE_REQUIRED_LINKS:
        score += _slot_score_for_index(slot_name, indexed)
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


def _unique_numbered_character_name(prefix):
    existing = {_component_short_name(character) for character in FBSystem().Scene.Characters}
    counter = 1
    while True:
        candidate = "{0}_{1}".format(prefix, counter)
        if candidate not in existing:
            return candidate
        counter += 1


def _is_animate_auto_character(character):
    return _component_short_name(character).startswith("animate_auto_")


def _is_aminate_generated_character(character):
    name = _component_short_name(character)
    return name.startswith("AminateMobu_") or name.startswith("animate_auto_")


def _rename_to_animate_auto(character):
    if character is None or _is_animate_auto_character(character):
        return character
    new_name = _unique_numbered_character_name("animate_auto")
    try:
        character.Name = new_name
    except Exception:
        try:
            character.LongName = new_name
        except Exception:
            pass
    return character


def _auto_map_target_character(namespace_label):
    current = _current_character()
    if current is not None and _is_animate_auto_character(current):
        return current, False
    if current is not None and _is_aminate_generated_character(current):
        return _rename_to_animate_auto(current), False
    character_name = _unique_numbered_character_name("animate_auto")
    return FBCharacter(character_name), True


def _disconnect_all_sources(prop):
    if prop is None:
        return
    try:
        prop.DisconnectAllSrc()
        return
    except Exception:
        pass
    for index in range(_property_src_count(prop) - 1, -1, -1):
        source = None
        try:
            source = prop.GetSrc(index)
        except Exception:
            source = None
        if source is None:
            continue
        try:
            prop.DisconnectSrc(source)
        except Exception:
            pass


def _map_model_to_slot(character, slot_name, model, replace_existing=True):
    prop = character.PropertyList.Find(slot_name, False)
    if prop is None or model is None:
        return False
    if replace_existing:
        _disconnect_all_sources(prop)
    try:
        prop.append(model)
        return True
    except Exception:
        try:
            prop.ConnectSrc(model)
            return True
        except Exception:
            return False


def _definition_store_load():
    path = _definition_store_path()
    if not os.path.isfile(path):
        return {"version": 1, "definitions": OrderedDict()}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle, object_pairs_hook=OrderedDict)
    except Exception:
        return {"version": 1, "definitions": OrderedDict()}
    definitions = payload.get("definitions")
    if not isinstance(definitions, dict):
        definitions = OrderedDict()
    payload["definitions"] = OrderedDict(definitions)
    payload["version"] = int(payload.get("version", 1) or 1)
    return payload


def _definition_store_save(payload):
    path = _definition_store_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return path


def _definition_names():
    return list(_definition_store_load().get("definitions", {}).keys())


def _sanitize_definition_name(name):
    cleaned = re.sub(r"\s+", " ", str(name or "").strip())
    return cleaned or "Character Definition"


def _current_definition_links(character):
    links = OrderedDict()
    if character is None:
        return links
    for slot_name in CHARACTER_SLOT_CANDIDATES:
        prop = character.PropertyList.Find(slot_name, False)
        model = _property_first_src(prop)
        if model is not None:
            links[slot_name] = _component_long_name(model)
    return links


def save_current_character_definition(name=None):
    character, error = _current_character_or_error()
    if error:
        _append_status(error["error"])
        return error
    definition_name = _sanitize_definition_name(name or _component_short_name(character))
    links = _current_definition_links(character)
    if not links:
        result = {"ok": False, "error": "Current character has no definition links to save."}
        _append_status(result["error"])
        return result
    payload = _definition_store_load()
    payload.setdefault("definitions", OrderedDict())
    payload["definitions"][definition_name] = OrderedDict([
        ("name", definition_name),
        ("saved_at", time.strftime("%Y-%m-%d %H:%M:%S")),
        ("source_character", character.LongName),
        ("characterized", bool(character.GetCharacterize())),
        ("core_link_count", _core_link_count(character)),
        ("links", links),
    ])
    path = _definition_store_save(payload)
    result = {
        "ok": True,
        "name": definition_name,
        "path": path,
        "link_count": len(links),
        "core_link_count": _core_link_count(character),
    }
    _append_status("Saved definition {0}: {1} link(s), core {2}/{3}.".format(definition_name, len(links), _core_link_count(character), len(CORE_REQUIRED_LINKS)))
    return result


def _find_definition_model(saved_name, slot_name, indexed):
    if saved_name:
        exact = FBFindModelByLabelName(saved_name)
        if exact is not None:
            return exact
        short_name = _short_name_from_long_name(saved_name)
        exact = FBFindModelByLabelName(short_name)
        if exact is not None:
            return exact
        normalized = _normalize_name(short_name)
        model = indexed.get(normalized)
        if model is not None:
            return model
    return _slot_match_for_index(slot_name, indexed)


def load_character_definition(name):
    definition_name = _sanitize_definition_name(name)
    payload = _definition_store_load()
    definition = payload.get("definitions", {}).get(definition_name)
    if not definition:
        result = {"ok": False, "error": "Definition not found: {0}".format(definition_name)}
        _append_status(result["error"])
        return result
    links = definition.get("links") or {}
    character, error = _current_character_or_error()
    if error:
        namespace_label = definition.get("namespace", "Scene")
        character, _created = _auto_map_target_character(namespace_label)
    FBApplication().CurrentCharacter = character
    was_characterized = bool(character.GetCharacterize())
    if was_characterized:
        try:
            character.SetCharacterizeOn(False)
        except Exception:
            pass
    namespace, indexed, _score = find_best_skeleton_namespace()
    mapped = OrderedDict()
    missing = []
    used_models = set()
    for slot_name, saved_model_name in links.items():
        model = _find_definition_model(saved_model_name, slot_name, indexed)
        if model is None or _component_long_name(model) in used_models:
            missing.append(slot_name)
            continue
        if _map_model_to_slot(character, slot_name, model):
            model_name = _component_long_name(model)
            mapped[slot_name] = model_name
            used_models.add(model_name)
    characterize_result = False
    characterize_error = ""
    try:
        characterize_result = bool(character.SetCharacterizeOn(True))
        characterize_error = character.GetCharacterizeError()
    except Exception as exc:
        characterize_error = str(exc)
    result = {
        "ok": True,
        "name": definition_name,
        "character_name": character.LongName,
        "namespace": namespace,
        "mapped_count": len(mapped),
        "missing": missing,
        "core_link_count": _core_link_count(character),
        "characterized": bool(character.GetCharacterize()),
        "characterize_result": characterize_result,
        "characterize_error": characterize_error,
    }
    lines = [
        "Loaded definition {0}".format(definition_name),
        "Character: {0}".format(character.LongName),
        "Mapped slots: {0}".format(len(mapped)),
        "Core links: {0}/{1}".format(_core_link_count(character), len(CORE_REQUIRED_LINKS)),
        "Characterized: {0}".format(bool(character.GetCharacterize())),
    ]
    if missing:
        lines.append("Missing slots: {0}".format(", ".join(missing[:12])))
    if characterize_error:
        lines.append("MotionBuilder warnings: {0}".format(str(characterize_error).strip().replace("\n", " | ")))
    _append_status("\n".join(lines))
    return result


def rename_character_definition(old_name, new_name):
    old_name = _sanitize_definition_name(old_name)
    new_name = _sanitize_definition_name(new_name)
    payload = _definition_store_load()
    definitions = payload.get("definitions", OrderedDict())
    if old_name not in definitions:
        result = {"ok": False, "error": "Definition not found: {0}".format(old_name)}
        _append_status(result["error"])
        return result
    if new_name in definitions and new_name != old_name:
        result = {"ok": False, "error": "Definition already exists: {0}".format(new_name)}
        _append_status(result["error"])
        return result
    definition = definitions.pop(old_name)
    definition["name"] = new_name
    definitions[new_name] = definition
    payload["definitions"] = definitions
    _definition_store_save(payload)
    result = {"ok": True, "old_name": old_name, "new_name": new_name}
    _append_status("Renamed definition {0} to {1}.".format(old_name, new_name))
    return result


def delete_character_definition(name):
    definition_name = _sanitize_definition_name(name)
    payload = _definition_store_load()
    definitions = payload.get("definitions", OrderedDict())
    if definition_name not in definitions:
        result = {"ok": False, "error": "Definition not found: {0}".format(definition_name)}
        _append_status(result["error"])
        return result
    definitions.pop(definition_name)
    payload["definitions"] = definitions
    _definition_store_save(payload)
    result = {"ok": True, "name": definition_name}
    _append_status("Deleted definition {0}.".format(definition_name))
    return result


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
    character, character_created = _auto_map_target_character(namespace_label)
    FBApplication().CurrentCharacter = character
    was_characterized = bool(character.GetCharacterize())
    if was_characterized:
        try:
            character.SetCharacterizeOn(False)
        except Exception:
            pass
    mapped = OrderedDict()
    used_models = set()
    for slot_name in CHARACTER_SLOT_CANDIDATES:
        model = _slot_match_for_index(slot_name, indexed, used_models=used_models)
        if model is None:
            continue
        if slot_name == "HipsTranslationLink" and _component_long_name(model) == mapped.get("HipsLink", ""):
            continue
        if _map_model_to_slot(character, slot_name, model):
            model_name = _component_long_name(model)
            mapped[slot_name] = model_name
            used_models.add(model_name)
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
        "character_created": bool(character_created),
        "was_characterized": bool(was_characterized),
        "mapped_slots": dict(mapped),
        "mapped_count": len(mapped),
        "core_link_count": _core_link_count(character),
        "characterized": bool(character.GetCharacterize()),
        "characterize_result": characterize_result,
        "characterize_error": characterize_error,
        "control_rig_result": control_rig_result,
    }
    report_lines = [
        "Auto Map Report",
        "Character: {0}".format(character.LongName),
        "Namespace: {0}".format(namespace_label),
        "Mapped slots: {0}".format(len(mapped)),
        "Core links: {0}/{1}".format(_core_link_count(character), len(CORE_REQUIRED_LINKS)),
        "Characterized: {0}".format(bool(character.GetCharacterize())),
        "Control rig: {0}".format(bool(control_rig_result)),
    ]
    if characterize_error:
        report_lines.append("MotionBuilder warnings: {0}".format(str(characterize_error).strip().replace("\n", " | ")))
    missing_core = []
    for slot_name in CORE_REQUIRED_LINKS:
        if slot_name not in mapped:
            missing_core.append(slot_name)
    if missing_core:
        report_lines.append("Missing core: {0}".format(", ".join(missing_core)))
    _append_status("\n".join(report_lines))
    _append_status(
        "Auto Map mapped {0} from {1} with {2} mapped slot(s), core {3}/{4}. Characterized: {5}.".format(
            character.LongName,
            namespace_label,
            len(mapped),
            _core_link_count(character),
            len(CORE_REQUIRED_LINKS),
            bool(character.GetCharacterize()),
        )
    )
    return result


def _current_character_or_error():
    character = _current_character()
    if character is None:
        return None, {"ok": False, "error": "No current character."}
    return character, None


def _character_key_models(character):
    models = OrderedDict()
    if character is None:
        return []
    for body_node in FBBodyNodeId.values.values():
        try:
            model = character.GetCtrlRigModel(body_node)
        except Exception:
            model = None
        if model is not None:
            models.setdefault(_component_long_name(model), model)
    if models:
        return list(models.values())
    for slot_name in CHARACTER_SLOT_CANDIDATES:
        prop = character.PropertyList.Find(slot_name, False)
        model = _property_first_src(prop)
        if model is not None:
            models.setdefault(_component_long_name(model), model)
    return list(models.values())


def _character_slot_model(character, slot_name):
    if character is None:
        return None
    prop = character.PropertyList.Find(slot_name, False)
    return _property_first_src(prop)


def _model_world_vector(model, transform_type):
    vector = FBVector3d()
    try:
        model.GetVector(vector, transform_type, True)
        return (float(vector[0]), float(vector[1]), float(vector[2]))
    except Exception:
        return None


def _model_world_translation(model):
    return _model_world_vector(model, FBModelTransformationType.kModelTranslation)


def _model_world_rotation(model):
    return _model_world_vector(model, FBModelTransformationType.kModelRotation)


def _set_model_world_rotation(model, rotation):
    try:
        model.SetVector(
            FBVector3d(float(rotation[0]), float(rotation[1]), float(rotation[2])),
            FBModelTransformationType.kModelRotation,
            True,
        )
        return True
    except Exception:
        return False


def _v_sub(left, right):
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _v_mul(value, scale):
    return (value[0] * scale, value[1] * scale, value[2] * scale)


def _v_dot(left, right):
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _v_cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _v_len(value):
    return math.sqrt(max(_v_dot(value, value), 0.0))


def _v_norm(value, fallback=None):
    length = _v_len(value)
    if length <= 0.000001:
        return fallback
    return (value[0] / length, value[1] / length, value[2] / length)


def _quat_norm(quat):
    length = math.sqrt(sum(item * item for item in quat))
    if length <= 0.000001:
        return (1.0, 0.0, 0.0, 0.0)
    return tuple(item / length for item in quat)


def _quat_mul(left, right):
    lw, lx, ly, lz = left
    rw, rx, ry, rz = right
    return (
        lw * rw - lx * rx - ly * ry - lz * rz,
        lw * rx + lx * rw + ly * rz - lz * ry,
        lw * ry - lx * rz + ly * rw + lz * rx,
        lw * rz + lx * ry - ly * rx + lz * rw,
    )


def _quat_from_vectors(source, target):
    source = _v_norm(source, (1.0, 0.0, 0.0))
    target = _v_norm(target, (1.0, 0.0, 0.0))
    dot = max(-1.0, min(1.0, _v_dot(source, target)))
    if dot < -0.999999:
        axis = _v_cross((1.0, 0.0, 0.0), source)
        if _v_len(axis) <= 0.000001:
            axis = _v_cross((0.0, 1.0, 0.0), source)
        axis = _v_norm(axis, (0.0, 0.0, 1.0))
        return (0.0, axis[0], axis[1], axis[2])
    cross = _v_cross(source, target)
    return _quat_norm((1.0 + dot, cross[0], cross[1], cross[2]))


def _quat_from_euler(rotation):
    x = math.radians(rotation[0]) * 0.5
    y = math.radians(rotation[1]) * 0.5
    z = math.radians(rotation[2]) * 0.5
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    return _quat_norm((
        cx * cy * cz + sx * sy * sz,
        sx * cy * cz - cx * sy * sz,
        cx * sy * cz + sx * cy * sz,
        cx * cy * sz - sx * sy * cz,
    ))


def _euler_from_quat(quat):
    w, x, y, z = _quat_norm(quat)
    sinr = 2.0 * (w * x + y * z)
    cosr = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr, cosr)
    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi * 0.5, sinp)
    else:
        pitch = math.asin(sinp)
    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny, cosy)
    return (math.degrees(roll), math.degrees(pitch), math.degrees(yaw))


def _evaluate_scene():
    try:
        FBSystem().Scene.Evaluate()
    except Exception:
        pass


def _align_model_segment(parent, child, desired_direction):
    parent_pos = _model_world_translation(parent)
    child_pos = _model_world_translation(child)
    rotation = _model_world_rotation(parent)
    desired = _v_norm(desired_direction)
    if parent_pos is None or child_pos is None or rotation is None or desired is None:
        return False
    current = _v_norm(_v_sub(child_pos, parent_pos))
    if current is None:
        return False
    delta = _quat_from_vectors(current, desired)
    result = _quat_mul(delta, _quat_from_euler(rotation))
    if not _set_model_world_rotation(parent, _euler_from_quat(result)):
        return False
    _evaluate_scene()
    return True


def _slot_pos(character, slot_name):
    model = _character_slot_model(character, slot_name)
    if model is None:
        return None
    return _model_world_translation(model)


def _direction_between(character, start_slot, end_slot, fallback=None):
    start = _slot_pos(character, start_slot)
    end = _slot_pos(character, end_slot)
    if start is None or end is None:
        return fallback
    return _v_norm(_v_sub(end, start), fallback)


def _tpose_reference_axes(character):
    up = (
        _direction_between(character, "HipsLink", "HeadLink")
        or _direction_between(character, "SpineLink", "HeadLink")
        or (0.0, 1.0, 0.0)
    )
    left = (
        _direction_between(character, "RightArmLink", "LeftArmLink")
        or _direction_between(character, "RightShoulderLink", "LeftShoulderLink")
        or _direction_between(character, "RightUpLegLink", "LeftUpLegLink")
        or (1.0, 0.0, 0.0)
    )
    # Remove vertical drift so arms become a true horizontal T relative to the body.
    left = _v_norm(_v_sub(left, _v_mul(up, _v_dot(left, up))), (1.0, 0.0, 0.0))
    forward = _v_norm(_v_cross(left, up), (0.0, 0.0, 1.0))
    left = _v_norm(_v_cross(up, forward), left)
    return {
        "up": up,
        "down": _v_mul(up, -1.0),
        "left": left,
        "right": _v_mul(left, -1.0),
    }


def _align_tpose_chain(character, slots, direction):
    aligned = 0
    for parent_slot, child_slot in zip(slots, slots[1:]):
        parent = _character_slot_model(character, parent_slot)
        child = _character_slot_model(character, child_slot)
        if parent is None or child is None:
            continue
        if _align_model_segment(parent, child, direction):
            aligned += 1
    return aligned


def _apply_skeleton_tpose(character):
    axes = _tpose_reference_axes(character)
    aligned = 0
    spine_slots = [
        "HipsLink",
        "SpineLink",
        "Spine1Link",
        "Spine2Link",
        "Spine3Link",
        "Spine4Link",
        "Spine5Link",
        "Spine6Link",
        "Spine7Link",
        "Spine8Link",
        "Spine9Link",
        "NeckLink",
        "Neck1Link",
        "Neck2Link",
        "HeadLink",
    ]
    left_arm = ["LeftShoulderLink", "LeftArmLink", "LeftForeArmLink", "LeftHandLink"]
    right_arm = ["RightShoulderLink", "RightArmLink", "RightForeArmLink", "RightHandLink"]
    left_leg = ["LeftUpLegLink", "LeftLegLink", "LeftFootLink", "LeftToeBaseLink"]
    right_leg = ["RightUpLegLink", "RightLegLink", "RightFootLink", "RightToeBaseLink"]
    aligned += _align_tpose_chain(character, spine_slots, axes["up"])
    aligned += _align_tpose_chain(character, left_arm, axes["left"])
    aligned += _align_tpose_chain(character, right_arm, axes["right"])
    aligned += _align_tpose_chain(character, left_leg, axes["down"])
    aligned += _align_tpose_chain(character, right_leg, axes["down"])
    return aligned


def make_tpose_on_frame_one(key_skeleton=True, key_control_rig=True):
    character, error = _current_character_or_error()
    if error:
        _append_status(error["error"])
        return error
    if not character.GetCharacterize():
        result = {"ok": False, "error": "Current character is not characterized. Auto Map Skeleton first."}
        _append_status(result["error"])
        return result

    player = FBPlayerControl()
    frame_one = FBTime(0, 0, 0, 1)
    try:
        player.Goto(frame_one, FBTimeReferential.kFBTimeReferentialEdit)
    except Exception:
        try:
            player.Goto(frame_one)
        except Exception:
            pass
    stance_pose_ok = True
    try:
        character.GoToStancePose(True, True)
    except Exception:
        try:
            character.GoToStancePose()
        except Exception:
            stance_pose_ok = False
    _evaluate_scene()
    aligned_segments = _apply_skeleton_tpose(character)

    keyed_models = 0
    keyed_channels = 0
    for model in _character_key_models(character):
        if not key_control_rig and _component_long_name(model).find("_Ctrl:") >= 0:
            continue
        for prop_name in CONTROL_RIG_PROPERTY_NAMES:
            keyed = _key_property_at_time(model.PropertyList.Find(prop_name), frame_one)
            if keyed:
                keyed_channels += keyed
        keyed_models += 1
    if key_skeleton:
        for slot_name in CHARACTER_SLOT_CANDIDATES:
            prop = character.PropertyList.Find(slot_name, False)
            model = _property_first_src(prop)
            if model is None:
                continue
            for prop_name in CONTROL_RIG_PROPERTY_NAMES:
                keyed_channels += _key_property_at_time(model.PropertyList.Find(prop_name), frame_one)

    try:
        player.Goto(frame_one, FBTimeReferential.kFBTimeReferentialEdit)
    except Exception:
        try:
            player.Goto(frame_one)
        except Exception:
            pass
    result = {
        "ok": True,
        "character_name": character.LongName,
        "frame": 1,
        "keyed_models": keyed_models,
        "keyed_channels": keyed_channels,
        "characterized": bool(character.GetCharacterize()),
        "stance_pose_ok": bool(stance_pose_ok),
        "aligned_segments": aligned_segments,
    }
    _append_status(
        "T-Pose Frame 1 keyed {0}: skeleton T-pose at frame 1 only, {1} segment(s), {2} model(s), {3} channel key(s).".format(
            character.LongName,
            aligned_segments,
            keyed_models,
            keyed_channels,
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


def _on_tpose_frame_one(control=None, event=None):
    make_tpose_on_frame_one(key_skeleton=True, key_control_rig=True)
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
            main_layout.setContentsMargins(6, 6, 6, 6)
            main_layout.setSpacing(5)
            header_layout = QtWidgets.QHBoxLayout()
            header_layout.setSpacing(5)
            header_text_layout = QtWidgets.QVBoxLayout()
            header_text_layout.setSpacing(0)
            self.header_title = QtWidgets.QLabel(TOOL_NAME)
            self.header_title.setObjectName("aminateMobuHeaderTitle")
            self.header_title.setToolTip("Main Aminate Mobu panel title.")
            header_text_layout.addWidget(self.header_title)
            self.header_subtitle = QtWidgets.QLabel("Scene cleanup  HIK mapping  setup warnings")
            self.header_subtitle.setObjectName("aminateMobuHeaderSubtitle")
            self.header_subtitle.setToolTip("Quick summary of the main Aminate Mobu jobs.")
            header_text_layout.addWidget(self.header_subtitle)
            header_layout.addLayout(header_text_layout, 1)
            self.theme_badge = QtWidgets.QLabel()
            self.theme_badge.setObjectName("aminateMobuThemeBadge")
            self.theme_badge.setToolTip("Shows which Aminate theme is active.")
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
            main_layout.addWidget(self._build_definition_manager_group())
            main_layout.addWidget(self._build_note_group())
            self.status_label = QtWidgets.QLabel("Ready.")
            self.status_label.setObjectName("mayaAnimWorkflowStatusLabel")
            self.status_label.setWordWrap(True)
            self.status_label.setToolTip("This line shows the newest Aminate status message.")
            main_layout.addWidget(self.status_label)
            self.status_memo = QtWidgets.QPlainTextEdit()
            self.status_memo.setReadOnly(True)
            self.status_memo.setObjectName("aminateMobuStatusMemo")
            self.status_memo.setToolTip("This area shows the full Aminate run history for the current session.")
            main_layout.addWidget(self.status_memo, 1)
            footer_layout = QtWidgets.QHBoxLayout()
            footer_layout.setContentsMargins(0, 0, 0, 0)
            footer_layout.setSpacing(6)
            self.brand_label = QtWidgets.QLabel(
                'Built by Amir. Follow Amir at <a href="{0}">followamir.com</a>.'.format(FOLLOW_AMIR_URL)
            )
            self.brand_label.setObjectName("mayaAnimWorkflowBrandLabel")
            self.brand_label.setOpenExternalLinks(False)
            self.brand_label.linkActivated.connect(self._open_follow_url)
            self.brand_label.setWordWrap(True)
            self.brand_label.setToolTip("Open followamir.com.")
            footer_layout.addWidget(self.brand_label, 1)
            self.version_label = QtWidgets.QLabel(TOOL_VERSION)
            self.version_label.setObjectName("mayaAnimWorkflowVersionLabel")
            self.version_label.setToolTip("Shows which Aminate Mobu build is loaded.")
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
            inner.setContentsMargins(8, 6, 8, 6)
            inner.setSpacing(2)
            title = QtWidgets.QLabel(title_text)
            title.setObjectName("mayaAnimWorkflowIntroTitle")
            body = QtWidgets.QLabel(body_text)
            body.setObjectName("mayaAnimWorkflowIntroBody")
            body.setWordWrap(True)
            inner.addWidget(title)
            inner.addWidget(body)
            return frame

        def _build_actions_group(self):
            group = QtWidgets.QGroupBox("Actions")
            group.setToolTip("Main Aminate tools for cleaning scenes, mapping rigs, and fixing setup issues.")
            layout = QtWidgets.QVBoxLayout(group)
            layout.setSpacing(5)
            marker_row = QtWidgets.QHBoxLayout()
            marker_row.setSpacing(5)
            marker_label = QtWidgets.QLabel("Prop Marker Base Name")
            marker_label.setToolTip("Name prefix Aminate uses when renaming animated prop markers.")
            marker_row.addWidget(marker_label)
            self.prop_marker_base_field = QtWidgets.QLineEdit(get_prop_marker_base_name())
            self.prop_marker_base_field.setPlaceholderText(DEFAULT_PROP_MARKER_BASE_NAME)
            self.prop_marker_base_field.setToolTip("Type the base name for animated prop markers such as Gun or Sword.")
            marker_row.addWidget(self.prop_marker_base_field, 1)
            layout.addLayout(marker_row)
            cleaner_grid = QtWidgets.QGridLayout()
            cleaner_grid.setHorizontalSpacing(5)
            cleaner_grid.setVerticalSpacing(4)
            cleaner_grid.addWidget(self._action_button("Refresh", _on_refresh), 0, 0)
            cleaner_grid.addWidget(self._action_button("Scene Cleaner", self._run_scene_cleaner), 0, 1)
            cleaner_grid.addWidget(self._action_button("Delete Cameras", _on_clean_cameras), 0, 2)
            cleaner_grid.addWidget(self._action_button("Delete Markers", self._run_marker_cleanup), 0, 3)
            layout.addLayout(cleaner_grid)
            setup_grid = QtWidgets.QGridLayout()
            setup_grid.setHorizontalSpacing(5)
            setup_grid.setVerticalSpacing(4)
            setup_grid.addWidget(self._action_button("Auto Map Skeleton", _on_auto_map), 0, 0)
            setup_grid.addWidget(self._action_button("Validate Character", _on_validate), 0, 1)
            setup_grid.addWidget(self._action_button("Body Part Mode", _on_body_part), 0, 2)
            setup_grid.addWidget(self._action_button("Full Body Mode", _on_full_body), 0, 3)
            setup_grid.addWidget(self._action_button("T-Pose Frame 1", _on_tpose_frame_one), 1, 0)
            layout.addLayout(setup_grid)
            history_row = QtWidgets.QHBoxLayout()
            history_row.setSpacing(5)
            history_row.addWidget(self._action_button("History Timeline", _on_history_timeline))
            history_row.addStretch(1)
            layout.addLayout(history_row)
            return group

        def _build_definition_manager_group(self):
            group = QtWidgets.QGroupBox("Definition Manager")
            group.setToolTip("Save, load, rename, and delete quick character definition presets.")
            layout = QtWidgets.QVBoxLayout(group)
            layout.setSpacing(5)

            selector_row = QtWidgets.QHBoxLayout()
            selector_row.setSpacing(5)
            self.definition_combo = QtWidgets.QComboBox()
            self.definition_combo.setToolTip("Pick a saved character definition preset.")
            selector_row.addWidget(self.definition_combo, 1)
            selector_row.addWidget(self._action_button("Refresh Definitions", self._refresh_definition_manager))
            layout.addLayout(selector_row)

            name_row = QtWidgets.QHBoxLayout()
            name_row.setSpacing(5)
            self.definition_name_field = QtWidgets.QLineEdit()
            self.definition_name_field.setPlaceholderText("Definition name")
            self.definition_name_field.setToolTip("Name used when saving or renaming a definition preset.")
            name_row.addWidget(self.definition_name_field, 1)
            layout.addLayout(name_row)

            button_grid = QtWidgets.QGridLayout()
            button_grid.setHorizontalSpacing(5)
            button_grid.setVerticalSpacing(4)
            button_grid.addWidget(self._action_button("Save Definition", self._save_definition), 0, 0)
            button_grid.addWidget(self._action_button("Load Definition", self._load_definition), 0, 1)
            button_grid.addWidget(self._action_button("Rename Definition", self._rename_definition), 0, 2)
            button_grid.addWidget(self._action_button("Delete Definition", self._delete_definition), 0, 3)
            layout.addLayout(button_grid)
            self._refresh_definition_manager()
            return group

        def _build_note_group(self):
            group = QtWidgets.QGroupBox("Notes")
            group.setToolTip("Short simple notes about how Aminate handles markers and cleanup.")
            layout = QtWidgets.QVBoxLayout(group)
            layout.setSpacing(3)
            hint = QtWidgets.QLabel(
                "Default markers with translation or rotation keys are treated as prop markers. Scene Cleaner keeps them, renames them with your chosen base name, and only deletes non-animated junk markers."
            )
            hint.setObjectName("aminateMobuGroupHint")
            hint.setWordWrap(True)
            hint.setToolTip("Explains what Aminate keeps, renames, and deletes during marker cleanup.")
            layout.addWidget(hint)
            return group

        def _action_button(self, caption, callback):
            button = QtWidgets.QPushButton(caption)
            tooltip = _easy_tooltip_text(caption, "QPushButton")
            if tooltip:
                button.setToolTip(tooltip)
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
            install_easy_motionbuilder_tooltips()

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

        def _selected_definition_name(self):
            combo = getattr(self, "definition_combo", None)
            if combo is not None and combo.currentText():
                return combo.currentText()
            return getattr(self, "definition_name_field", None).text() if getattr(self, "definition_name_field", None) is not None else ""

        def _refresh_definition_manager(self):
            combo = getattr(self, "definition_combo", None)
            if combo is None:
                return
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            names = _definition_names()
            combo.addItems(names)
            if current in names:
                combo.setCurrentText(current)
            combo.blockSignals(False)
            if getattr(self, "definition_name_field", None) is not None and combo.currentText():
                self.definition_name_field.setText(combo.currentText())

        def _save_definition(self):
            name = getattr(self, "definition_name_field", None).text() if getattr(self, "definition_name_field", None) is not None else ""
            result = save_current_character_definition(name)
            self._refresh_definition_manager()
            if result.get("ok") and getattr(self, "definition_combo", None) is not None:
                self.definition_combo.setCurrentText(result.get("name", ""))
            _refresh_dashboard()

        def _load_definition(self):
            load_character_definition(self._selected_definition_name())
            _refresh_dashboard()

        def _rename_definition(self):
            old_name = self._selected_definition_name()
            new_name = getattr(self, "definition_name_field", None).text() if getattr(self, "definition_name_field", None) is not None else ""
            result = rename_character_definition(old_name, new_name)
            self._refresh_definition_manager()
            if result.get("ok") and getattr(self, "definition_combo", None) is not None:
                self.definition_combo.setCurrentText(result.get("new_name", ""))
            _refresh_dashboard()

        def _delete_definition(self):
            delete_character_definition(self._selected_definition_name())
            self._refresh_definition_manager()
            _refresh_dashboard()

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
    row.Add(_button("T-Pose Frame 1", _on_tpose_frame_one, color=(0.24, 0.34, 0.40)), 150)
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
    ensure_default_ui_snapshot()
    _ensure_aminate_launcher_toolbar()
    install_easy_motionbuilder_tooltips()
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
        install_easy_motionbuilder_tooltips()
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
    "make_tpose_on_frame_one",
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
