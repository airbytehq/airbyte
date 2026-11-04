# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

sys.path.append(str(Path(__file__).parent.parent))
