# Aminate Motionbuilder

Private MotionBuilder repo for Aminate Mobu.

## Included

- `aminate_mobu.py`
- `aminate_mobu_history.py`
- MotionBuilder smoke scripts
- startup launcher wrapper
- student package output

## Install startup hook

Run:

```bash
python install_motionbuilder_startup.py
```

That writes the MotionBuilder startup bootstrap into every detected MotionBuilder version folder under `C:\Users\Amir Mansaray\Documents\MB\<version>\config\PythonStartup`.

Current machine example:

`C:\Users\Amir Mansaray\Documents\MB\2026\config\PythonStartup\aminate_mobu_startup.py`

## Launch in MotionBuilder

Use:

```bash
python launch_aminate_mobu.py
```

Or restart MotionBuilder after installing the startup hook. The host UI should show an `Aminate` toolbar button and a dockable `Aminate Mobu` panel.

## Compatibility

- startup install targets all detected MotionBuilder version folders, not just 2026
- Qt import path supports `PySide6` first and falls back to `PySide2`
- launch path uses MotionBuilder host Qt docking when available and native tool fallback otherwise
