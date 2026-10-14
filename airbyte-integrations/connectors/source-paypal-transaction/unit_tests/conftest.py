# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path


# The CDK resolves `source_declarative_manifest.components` to the connector's components.py
# only when the connector directory is importable.
sys.path.insert(0, str(Path(__file__).parent.parent))

pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]
