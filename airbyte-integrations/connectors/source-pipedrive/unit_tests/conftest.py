# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

import pytest


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")


def _get_connector_dir() -> Path:
    """Resolve the connector directory.

    In CI the connector is copied into `/airbyte/integration_code/source_declarative_manifest/`.
    Locally the tests live in `<connector>/unit_tests/`.
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


CONNECTOR_DIR = _get_connector_dir()
MANIFEST_PATH = CONNECTOR_DIR / "manifest.yaml"

# Allow `source_declarative_manifest.components.*` class names to resolve to the local components.py
sys.path.insert(0, str(CONNECTOR_DIR))
# Allow test files to import sibling helper modules regardless of the pytest invocation directory
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
