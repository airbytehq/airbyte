#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
from pathlib import Path

from ci_common_utils import Logger

LOGGER = Logger()

ROOT_DIR = Path(os.getcwd())
while str(ROOT_DIR) != "/" and not (ROOT_DIR / "gradlew").is_file():
    ROOT_DIR = ROOT_DIR.parent
if str(ROOT_DIR) == "/":
    LOGGER.critical("this script must be executed into the Airbyte repo only")
