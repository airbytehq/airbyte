# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


_CI_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_SOURCE_PATH = _CI_PATH if _CI_PATH.exists() else Path(__file__).parent.parent
_YAML_FILE_PATH = _SOURCE_PATH / "manifest.yaml"


@pytest.fixture
def manifest() -> dict:
    return yaml.safe_load(_YAML_FILE_PATH.read_text())
