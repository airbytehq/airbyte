#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path
from typing import Any, Mapping

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CONNECTOR_DIR = Path(__file__).parent.parent
_UNIT_TESTS_DIR = Path(__file__).parent

# The connector's manifest references custom components as
# `source_declarative_manifest.components.<Class>`. When resolving those classes the CDK falls
# back to importing a top-level `components` module, so the connector root (which holds
# `components.py`) must be importable. The `unit_tests` directory is added so sibling helper
# modules (e.g. `_helpers`) import whether pytest runs from the connector root (CI) or from
# `unit_tests/` (local development).
for _path in (_CONNECTOR_DIR, _UNIT_TESTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@pytest.fixture
def config() -> Mapping[str, Any]:
    return {
        "credentials": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
        },
    }
