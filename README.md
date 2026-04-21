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

That writes the MotionBuilder startup bootstrap into:

`C:\Users\Amir Mansaray\Documents\MB\2026\config\PythonStartup\aminate_mobu_startup.py`

## Launch in MotionBuilder

Use:

```bash
python launch_aminate_mobu.py
```

Or restart MotionBuilder after installing the startup hook. The host UI should show an `Aminate` toolbar button and a dockable `Aminate Mobu` panel.
