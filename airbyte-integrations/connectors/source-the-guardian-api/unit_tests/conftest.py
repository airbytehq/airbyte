# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def connector_dir():
    """Return the connector's root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def components_module(connector_dir):
    """
    Load and return the components module from the connector directory.
    This makes custom components available to all test files.
    """
    components_path = connector_dir / "components.py"
    if not components_path.exists():
        return None

    spec = importlib.util.spec_from_file_location("components", components_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.fixture(scope="session")
def manifest_path(connector_dir):
    """Return the path to the connector's manifest file."""
    return connector_dir / "manifest.yaml"
