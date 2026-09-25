"""
PHANI AI - Legacy Entrypoint Bridge.
Maintained for backward compatibility, routing to the modular Phani AI Platform.
"""

import sys
from pathlib import Path

# Ensure workspace directory is in python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Execute main platform application
import app