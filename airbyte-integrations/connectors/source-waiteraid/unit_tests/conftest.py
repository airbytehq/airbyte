# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(config) -> YamlDeclarativeSource:
    source_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_folder.exists():
        source_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(source_folder / "manifest.yaml"), catalog=CatalogBuilder().build(), config=config)
