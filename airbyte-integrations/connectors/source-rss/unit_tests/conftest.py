# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_folder() -> Path:
    """Return the folder holding manifest.yaml, in CI (Docker) or locally."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_folder()
YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

# Allows `source_declarative_manifest.components.*` references in the manifest to
# resolve to <connector_dir>/components.py during tests.
sys.path.append(str(_SOURCE_FOLDER_PATH))
