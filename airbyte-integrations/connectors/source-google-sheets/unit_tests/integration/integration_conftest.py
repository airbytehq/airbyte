#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path


# Override the manifest path for integration tests
# Since integration tests are run from unit_tests/integration/,
# we need to go up one more level to reach the connector root
def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
