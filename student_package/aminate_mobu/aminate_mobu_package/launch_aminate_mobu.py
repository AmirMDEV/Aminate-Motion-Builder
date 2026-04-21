from __future__ import absolute_import, division, print_function

import importlib
import os
import sys


MODULE_ROOT = os.path.dirname(os.path.abspath(__file__))


def launch():
    while MODULE_ROOT in sys.path:
        sys.path.remove(MODULE_ROOT)
    sys.path.insert(0, MODULE_ROOT)
    import aminate_mobu

    importlib.reload(aminate_mobu)
    return aminate_mobu.launch_aminate_mobu()


if __name__ == "__main__":
    launch()

