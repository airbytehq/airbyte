# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def get_source(config: dict, catalog: ConfiguredAirbyteCatalog) -> YamlDeclarativeSource:
    source_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_path.exists():
        source_path = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(source_path / "manifest.yaml"), config=config, catalog=catalog)
