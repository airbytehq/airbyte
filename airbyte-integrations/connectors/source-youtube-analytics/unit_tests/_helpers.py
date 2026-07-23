# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-youtube-analytics` unit tests."""

import importlib.util
import sys
import types
from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


def _get_connector_dir() -> Path:
    """Resolve the connector's root directory.

    In CI the connector is copied into `/airbyte/integration_code/source_declarative_manifest/`.
    Locally, tests are run from the connector's `unit_tests/` directory, so the connector root
    is one directory up.
    """
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_CONNECTOR_DIR = _get_connector_dir()
_MANIFEST_PATH = _CONNECTOR_DIR / "manifest.yaml"


def _register_custom_components() -> None:
    """Make `components.py` importable as `source_declarative_manifest.components`.

    The manifest references custom components via the dotted path
    `source_declarative_manifest.components.<Class>`, which is how they are packaged on the
    `source-declarative-manifest` base image. This registers the connector's local
    `components.py` under that module path so `YamlDeclarativeSource` can resolve them.
    """
    if "source_declarative_manifest.components" in sys.modules:
        return

    package = sys.modules.get("source_declarative_manifest")
    if package is None:
        package = types.ModuleType("source_declarative_manifest")
        package.__path__ = []  # mark as a package
        sys.modules["source_declarative_manifest"] = package

    spec = importlib.util.spec_from_file_location(
        "source_declarative_manifest.components", str(_CONNECTOR_DIR / "components.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["source_declarative_manifest.components"] = module
    package.components = module


def get_source(config, state=None) -> YamlDeclarativeSource:
    """Instantiate a `YamlDeclarativeSource` for `source-youtube-analytics` using its manifest."""
    _register_custom_components()
    catalog = CatalogBuilder().build()
    state = state if state is not None else StateBuilder().build()
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=config,
        state=state,
    )
