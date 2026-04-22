# Changelog

## 2026-04-22

- Rebuilt the `Modern` theme from the captured clean-host reference and generated concept with a darker graphite and steel-blue token set across host chrome and Aminate-owned surfaces while leaving the native `MotionBuilder` restore path untouched
- Pushed the `Modern` theme closer to the concept again with darker palette roles, broader dock child surface styling, and abstract-button coverage for remaining host chrome that still looked native

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
