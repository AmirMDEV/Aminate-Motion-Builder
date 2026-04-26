Aminate Motion Builder install files

Fast install in MotionBuilder:
1. Unzip this package.
2. Open the Aminate_Motion_Builder_Install_Files folder.
3. Drag Install_Aminate_Motion_Builder.py into the MotionBuilder viewport.
4. Aminate installs its startup hook, opens the Aminate panel, and switches to the Modern UI.

Package layout:
- Main folder: only the drag-and-drop installer file plus the install_files folder.
- install_files: all runtime scripts, assets, license, manifest, and this README.

Manual fallback:
1. Open Python Tools or the Python Editor in MotionBuilder.
2. Run install_files\install_motionbuilder_startup.py to install the startup hook.
3. Run install_files\launch_aminate_mobu.py to open Aminate immediately.

Current functions:
- Scene Cleaner removes junk scene objects, user cameras, and unused unlabeled markers while preserving useful animated prop markers.
- Auto Map Skeleton reads the selected skeleton, bone, or mesh, creates animate_auto_1, animate_auto_2, etc., and fills a HumanIK character definition.
- T-Pose Frame 0 keys a MotionBuilder-friendly T-pose on frame 0 for retargeting and character-definition cleanup.
- Definition Manager saves, loads, renames, and removes reusable skeleton definitions.
- Constraints Manager lists useful MotionBuilder constraints, explains when to use them, helps rename them, keys them, and opens bake/plot options.
- Prop Take Offset Manager stores selected prop constraint offsets per take so prop setups can survive different prop starting positions.
- History Timeline saves full-scene MotionBuilder snapshots with restore, milestones, branching, snapshot caps, and Auto History.
- Modern UI restyles Aminate and themeable MotionBuilder chrome while keeping the default MotionBuilder UI restore path available.
- Rich tooltips explain buttons and tool icons in plain language.
- Startup install targets all detected MotionBuilder version folders under Documents\MB.

Credit: Amir Mansaray
GitHub: https://github.com/AmirMDEV/Aminate-Motion-Builder
Follow Amir: https://followamir.com
Donate: https://www.paypal.com/donate/?hosted_button_id=2U2GXSKFJKJCA
Full license: see LICENSE
