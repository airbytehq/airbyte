# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import importlib.util
import sys
from pathlib import Path

pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

CONNECTOR_DIR = Path(__file__).parent.parent
COMPONENTS_PATH = CONNECTOR_DIR / "components.py"

components_spec = importlib.util.spec_from_file_location("source_declarative_manifest.components", COMPONENTS_PATH)
if components_spec and components_spec.loader:
    components_module = importlib.util.module_from_spec(components_spec)
    sys.modules["source_declarative_manifest.components"] = components_module
    components_spec.loader.exec_module(components_module)
