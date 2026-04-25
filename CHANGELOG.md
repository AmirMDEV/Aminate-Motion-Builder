# Changelog

## 2026-04-25

- Replaced the stale MotionBuilder theme restore with a deterministic dark native-style host fallback so the File/Edit toolbar and standard buttons no longer drop to the old Windows-style chrome
- Fixed MotionBuilder startup so Aminate opens directly in the Modern UI, and changed MotionBuilder theme restore to use the live native baseline instead of forcing an old saved layout snapshot
- Added compressed animated constraint tutorial GIF previews with a hover/selection preview panel in Constraints Manager plus a reusable generator script for refreshing the demo assets
- Filtered Constraints Manager to show only user-facing asset-browser constraints such as Position, Rotation, Aim, Parent-Child, Relation, Chain IK, Spline IK, Expression, Path, and Rigid Body, while hiding HIK solvers and character internals
- Added selected-skeleton scoping so Aminate requires a chosen skeleton hierarchy in multi-skeleton scenes, then Auto Map and T-Pose operate only on that selected hierarchy
- Added a Constraints Manager panel for listing MotionBuilder constraints, renaming user constraints to readable Aminate names, keying useful constraint properties at the current time, opening bake/plot options, and using clearer Save To Skeleton / Save To Control Rig language
- Moved the automatic skeleton T-pose to frame 0, stopped rotating feet through toe links, added finger alignment, added green-check status feedback, made Aminate open in Modern by default, and added a collapsible scrollable dock panel for smaller resize widths

## 2026-04-24

- Fixed `T-Pose Frame 1` for skeleton-mode characters by rotating mapped skeleton body segments into a calculated T-pose at frame 1, keying the skeleton channels, and naming Auto Map output as `animate_auto_1`, `animate_auto_2`, and so on
- Improved Auto Map Skeleton with scored humanoid matching for common naming styles such as Unreal side suffixes, Mixamo/HIK-style aliases, Blender side markers, fingers, toes, twist bones, and existing-character remapping
- Added Auto Map reporting plus a single-button `T-Pose Frame 1` action that sends the current characterized character to MotionBuilder stance pose at frame 1 and keys the pose there for mocap and mesh prep
- Added a Definition Manager for saving, loading, renaming, deleting, and refreshing reusable character definition presets from inside Aminate Mobu

## 2026-04-22

- Rebuilt the `Modern` theme from the captured clean-host reference and generated concept with a darker graphite and steel-blue token set across host chrome and Aminate-owned surfaces while leaving the native `MotionBuilder` restore path untouched
- Pushed the `Modern` theme closer to the concept again with darker palette roles, broader dock child surface styling, and abstract-button coverage for remaining host chrome that still looked native
- Tuned the core modern palette and shared host surfaces again so custom-painted viewer and transport lanes inherit a darker blue-gray value range closer to the concept image
- Tightened the Aminate dock rhythm in `Modern` with denser header typography, smaller card padding, more compact action-grid spacing, and a shorter footer so the right panel reads closer to the host concept

## 2026-04-21

- Initial private MotionBuilder repo created
- Added dockable Aminate Mobu host panel
- Added MotionBuilder toolbar button entry
- Added startup bootstrap installer path
- Copied current MotionBuilder package and smoke scripts
- Expanded startup installer to target all detected MotionBuilder version folders
- Documented broader MotionBuilder compatibility strategy
- Retuned the modern MotionBuilder theme to match the supplied full-app reference image more closely
- Refined lower-half modern theme parity for transport controls, pane tabs, splitters, group boxes, and list regions
- Refined modern theme iconography for toolbar chrome, dropdown lanes, separators, and control chips
- Tightened modern theme typography and spacing across the Aminate dock header, cards, button grids, notes, and status areas
- Added an imagegen-based Aminate launcher icon asset and wired the MotionBuilder toolbar button to use text plus icon with package-safe asset copying
- Added the exact full-size transparent Aminate logo PNG at repo root, generated a matching SVG wrapper version, and regenerated toolbar icon sizes from that source
- Added a host-wide easy tooltip pass for Qt-visible MotionBuilder menus, tabs, buttons, panels, and all Aminate controls, and restored the live Aminate launcher plus dock in MotionBuilder
- Corrected theme behavior so `MotionBuilder` restores true native host styling and `Modern` owns the custom Aminate and host chrome restyle
- Added baseline caching and stale-modern recovery so reloading the plugin no longer causes the `MotionBuilder` theme to capture the old modern host restyle as its default
- Retuned modern-theme buttons across the Aminate panel, launcher, host toolbar controls, and donate CTA so the custom mode reads as a more intentionally modern dark UI
- Retuned modern-theme tab headers across both host MotionBuilder panes and Aminate-local tabs with rounder shapes, clearer hover hierarchy, and stronger selected-state separation
- Retuned remaining modern-theme chrome such as dock title bars, dock utility buttons, combo dropdown lanes, popup lists, and status seams to replace more of the lingering native default styling
- Tightened the remaining modern-theme utility chrome again with stronger group-box title chips, menu pressed and separator states, spin-box subcontrols, and status-label styling to reduce the last obvious stock Qt surfaces
- Tightened lower-pane interiors with denser search-field styling, stronger header treatment, and clearer list and tree row hierarchy so the lower workspace matches the polished upper chrome
- Added dock-scoped compact utility overrides so transport, key-control, and other narrow dock controls feel tighter and less like generic full-size form controls
- Added a live MotionBuilder UI snapshot baseline so the `MotionBuilder` theme button can restore the captured current layout instead of only relying on the stock app baseline
- Added automatic one-time baseline layout capture on Aminate startup plus a no-input UIA reference capture tool for the currently open MotionBuilder window
- Added a telnet-friendly live verification helper that proves the captured current MotionBuilder layout restores after switching to Modern and back
- Captured a pure host MotionBuilder full-window reference without Aminate open and generated a modern full-window concept mock that preserves the same layout while modernizing iconography and chrome
