# Aminate Mobu 0.1 Beta

This is the first public beta of Aminate Mobu for Autodesk MotionBuilder.

## Premiere Video

`40_Seconds_to_Mocap.mp4` is the main release video. It shows the intended quick flow from imported motion capture to a cleaner, character-ready MotionBuilder setup.

## What Aminate Can Do

- **Drag and drop installer**: unzip the release, then drag `Install_Aminate_Mobu.py` into the MotionBuilder viewport. Aminate installs the startup hook, opens the panel, and loads on future MotionBuilder launches.
- **Scene Cleaner**: removes common import junk, user cameras, and unused unlabeled markers while preserving markers that appear to carry useful prop animation.
- **Auto Map Skeleton**: reads the selected skeleton, bone, or skinned mesh and creates numbered MotionBuilder character definitions such as `animate_auto_1`, `animate_auto_2`, and `animate_auto_3`.
- **T-Pose Frame 0**: keys a MotionBuilder-friendly T-pose on frame 0 so source and target characters can be prepared for cleaner retargeting.
- **Definition Manager**: saves, loads, renames, and removes reusable skeleton definitions from inside Aminate.
- **Constraints Manager**: focuses on the useful MotionBuilder constraint assets, adds short visual explanations, supports easier naming, and helps with keying and bake/plot workflows.
- **Modern UI**: switches Aminate into a cleaner modern MotionBuilder-style UI while preserving the default MotionBuilder UI return path.
- **Rich tooltips**: explains buttons and icon-only tools in plain language so the workflow is easier to learn.
- **History Timeline**: saves full-scene snapshots, restores snapshots, supports milestones, branching, snapshot caps, and Auto History.

## How To Install

1. Download `Aminate_Mobu_v0.1_BETA.zip`.
2. Unzip it somewhere convenient.
3. Drag `Install_Aminate_Mobu.py` into the MotionBuilder viewport.
4. Accept the install message.
5. Restart MotionBuilder when you want to confirm Aminate loads automatically.

## How To Use

1. Open MotionBuilder.
2. Aminate opens with the Modern UI by default after installation.
3. Select a skeleton, any bone in a skeleton, or a skinned mesh.
4. Use **Auto Map Skeleton** to create a MotionBuilder character definition.
5. Use **T-Pose Frame 0** to place the selected character into a frame-zero T-pose.
6. Use **Scene Cleaner** before characterization or retargeting when an imported scene contains cameras, junk markers, or capture leftovers.
7. Use **Definition Manager** to reuse known-good mappings.
8. Use **Constraints Manager** when setting up parent, position, rotation, aim, IK, path, or relation-style constraint workflows.

## Beta Notes

- This is proprietary source-available software, not an open-source project.
- Forking, modifying, republishing modified copies, and derivative versions are not allowed without written permission.
- The package is intended for MotionBuilder users testing the beta workflow on real character and mocap scenes.
