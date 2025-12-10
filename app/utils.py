import os
import subprocess
from dunebugger_logging import logger

def is_raspberry_pi():
    try:
        with open("/proc/device-tree/model") as model_file:
            model = model_file.read()
            if "Raspberry Pi" in model:
                return True
            else:
                return False
    except Exception:
        return False

def validate_path(path):
    if os.path.exists(path):
        return True
    else:
        return False
