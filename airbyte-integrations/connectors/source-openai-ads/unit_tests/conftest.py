# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

# The manifest names `source_declarative_manifest.components`; the CDK falls back to `components` on the path in tests.
sys.path.append(str(Path(__file__).parent.parent))
