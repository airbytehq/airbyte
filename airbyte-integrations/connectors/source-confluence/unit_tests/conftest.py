# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")

# Ensure the `unit_tests/` directory is on `sys.path` so sibling modules can be imported
# by test files whether pytest is invoked from the connector root (CI) or from
# `unit_tests/` itself (local development).
_UNIT_TESTS_DIR = Path(__file__).parent
if str(_UNIT_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_UNIT_TESTS_DIR))
