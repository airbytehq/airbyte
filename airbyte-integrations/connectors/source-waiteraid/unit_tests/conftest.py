# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CI_MANIFEST_PATH = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
_MANIFEST_PATH = _CI_MANIFEST_PATH if _CI_MANIFEST_PATH.exists() else Path(__file__).resolve().parents[1] / "manifest.yaml"


def get_source(config, state=None) -> YamlDeclarativeSource:
    source = YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config,
        state=state if state is not None else StateBuilder().build(),
    )
    source._constructor._disable_cache = True
    return source
