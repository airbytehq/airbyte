# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

# The following fixtures are used to load a manifest-only connector's components module and manifest file.
# They can be accessed from any test file in the connector's unit_tests directory by importing them as follows:

# from airbyte_cdk.test.utils.manifest_only_fixtures import components_module, connector_dir, manifest_path

# individual components can then be referenced as: components_module.<CustomComponentClass>


@pytest.fixture(scope="session")
def connector_dir(request: pytest.FixtureRequest) -> Path:
    """Return the connector's root directory."""

    current_dir = Path(request.config.invocation_params.dir)

    # If the tests are run locally from the connector's unit_tests directory, return the parent (connector) directory
    if current_dir.name == "unit_tests":
        return current_dir.parent
    # In CI, the tests are run from the connector directory itself
    return current_dir


@pytest.fixture(scope="session")
def components_module(connector_dir: Path) -> ModuleType | None:
    """Load and return the components module from the connector directory.

    This assumes the components module is located at <connector_dir>/components.py.
    """
    components_path = connector_dir / "components.py"
    if not components_path.exists():
        return None

    components_spec = importlib.util.spec_from_file_location("components", components_path)
    if components_spec is None:
        return None

    components_module = importlib.util.module_from_spec(components_spec)
    if components_spec.loader is None:
        return None

    components_spec.loader.exec_module(components_module)
    return components_module


@pytest.fixture(scope="session")
def manifest_path(connector_dir: Path) -> Path:
    """Return the path to the connector's manifest file."""
    path = connector_dir / "manifest.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found at {path}")
    return path
