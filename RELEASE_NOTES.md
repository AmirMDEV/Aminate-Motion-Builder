# Aminate Motion Builder 0.1 Beta

This is the first public beta of Aminate Motion Builder for Autodesk MotionBuilder.

## July 2026 Update

- Added five real, clickable workflow tabs for Scene Cleanup, HIK Mapping, Setup Warnings, Constraints, and History.
- Wired `Use Selected Skeleton`, Auto Map, setup checks, constraint tools, and History into their visible workflow pages.
- Fixed Modern-to-MotionBuilder switching so the cached native stylesheet, palette, main-window geometry, and dock geometry are restored.
- Removed live plugin reloads and application-wide Qt style replacement after reproducing MotionBuilder access violations during dock teardown.
- Made repeated launches, dock close/reopen, History close/reopen, normal shutdown, and installed-package startup stable.
- Changed updates to merge files in place and keep the already loaded session running; restart MotionBuilder once to activate newly copied code.
- Fixed the drag-and-drop installer success message and validated the actual release ZIP, not only the source tree.

## Quick Install

1. Download `Aminate_Motion_Builder_v0.1_BETA.zip` from this release.
2. Unzip it.
3. Open the `Aminate_Motion_Builder_Install_Files` folder.
4. Drag `Install_Aminate_Motion_Builder.py` into the MotionBuilder viewport.
5. Aminate opens immediately on a first install and installs its startup hook for future MotionBuilder launches.
6. If you are updating an already loaded copy, restart MotionBuilder once to activate the new files.

## Premiere Video

`40_Seconds_to_Mocap.mp4` is the main release video. It shows the intended quick flow from imported motion capture to a cleaner, character-ready MotionBuilder setup.

## Feature Videos

- `40_Seconds_to_Mocap.mp4` is the premiere video.
- `Mobu_Automap_and_Tpose.mp4` shows Auto Map Skeleton and T-Pose Frame 0.
- `Mobu_Scene_Cleaner.mp4` shows scene cleanup.

## Screenshots

![Scene Cleanup](https://github.com/AmirMDEV/Aminate-Motion-Builder/releases/download/v0.1-beta/screenshot_scene_cleanup_workflow.png)

![HIK Mapping](https://github.com/AmirMDEV/Aminate-Motion-Builder/releases/download/v0.1-beta/screenshot_hik_mapping_workflow.png)

![Setup Warnings](https://github.com/AmirMDEV/Aminate-Motion-Builder/releases/download/v0.1-beta/screenshot_setup_warnings_workflow.png)

![Constraints Manager](https://github.com/AmirMDEV/Aminate-Motion-Builder/releases/download/v0.1-beta/screenshot_constraints_manager_workflow.png)

![History Timeline](https://github.com/AmirMDEV/Aminate-Motion-Builder/releases/download/v0.1-beta/screenshot_history_timeline.png)

## What Aminate Can Do

- **Real workflow tabs**: switches reliably between Scene Cleanup, HIK Mapping, Setup Warnings, Constraints, and History, even in a narrow MotionBuilder dock.
- **Drag and drop installer**: unzip the release, open the install folder, then drag `Install_Aminate_Motion_Builder.py` into the MotionBuilder viewport. Aminate installs the startup hook, opens the panel, and loads on future MotionBuilder launches.
- **Scene Cleaner**: removes common import junk, user cameras, and unused unlabeled markers while preserving markers that appear to carry useful prop animation.
- **Auto Map Skeleton**: reads the selected skeleton, bone, or skinned mesh and creates numbered MotionBuilder character definitions such as `animate_auto_1`, `animate_auto_2`, and `animate_auto_3`.
- **T-Pose Frame 0**: keys a MotionBuilder-friendly T-pose on frame 0 so source and target characters can be prepared for cleaner retargeting.
- **Setup Warnings**: checks the current HumanIK setup, records lock/keying-mode warnings, and switches between Body Part and Full Body keying.
- **Definition Manager**: saves, loads, renames, and removes reusable skeleton definitions from inside Aminate.
- **Constraints Manager**: focuses on the useful MotionBuilder constraint assets, adds short visual explanations, supports easier naming, and helps with keying and bake/plot workflows.
- **Prop Take Offset Manager**: previews and stores selected prop constraint offsets per take so props can start in different places without forcing an immediate bake loop on every take.
- **Modern UI**: switches Aminate into a cleaner modern MotionBuilder-style UI, then restores the exact cached native MotionBuilder stylesheet and palette when you switch back.
- **Rich tooltips**: explains buttons and icon-only tools in plain language so the workflow is easier to learn.
- **History Timeline**: saves full-scene snapshots, restores snapshots, supports milestones, branching, snapshot caps, and Auto History.

## How To Install

1. Download `Aminate_Motion_Builder_v0.1_BETA.zip`.
2. Unzip it somewhere convenient.
3. Open the `Aminate_Motion_Builder_Install_Files` folder.
4. Drag `Install_Aminate_Motion_Builder.py` into the MotionBuilder viewport.
5. Accept the install message.
6. Restart MotionBuilder once after an update, or whenever you want to confirm automatic startup.

## How To Use

1. Open MotionBuilder.
2. Aminate opens with the Modern UI by default after installation.
3. Choose the Scene Cleanup, HIK Mapping, Setup Warnings, Constraints, or History tab for the job you are doing.
4. Select a skeleton, any bone in a skeleton, or a skinned mesh.
5. Use **Auto Map Skeleton** to create a MotionBuilder character definition.
6. Use **T-Pose Frame 0** to place the selected character into a frame-zero T-pose.
7. Use **Scene Cleaner** before characterization or retargeting when an imported scene contains cameras, junk markers, or capture leftovers.
8. Use **Setup Warnings** to check the current character and choose Body Part or Full Body keying.
9. Use **Definition Manager** to reuse known-good mappings.
10. Use **Constraints Manager** when setting up parent, position, rotation, aim, IK, path, or relation-style constraint workflows.
11. Use **Prop Take Offset Manager** when a prop constraint works on one take but needs a different offset on another take.

## Beta Notes

- This is proprietary source-available software, not an open-source project.
- Forking, modifying, republishing modified copies, and derivative versions are not allowed without written permission.
- The package is intended for MotionBuilder users testing the beta workflow on real character and mocap scenes.
