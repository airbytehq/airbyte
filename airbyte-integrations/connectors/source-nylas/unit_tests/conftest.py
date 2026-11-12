# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(config: Mapping[str, Any]) -> YamlDeclarativeSource:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    source_path = ci_path if ci_path.exists() else Path(__file__).parent.parent
    return YamlDeclarativeSource(
        path_to_yaml=str(source_path / "manifest.yaml"), catalog=CatalogBuilder().build(), config=config, state=[]
    )
