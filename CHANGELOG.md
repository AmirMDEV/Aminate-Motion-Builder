# Changelog

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
