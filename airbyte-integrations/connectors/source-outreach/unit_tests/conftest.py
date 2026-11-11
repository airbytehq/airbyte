# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path


CONNECTOR_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CONNECTOR_DIR))
