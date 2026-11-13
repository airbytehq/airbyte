# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


def get_source(config: dict[str, str]) -> YamlDeclarativeSource:
    source_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not source_folder.exists():
        source_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(source_folder / "manifest.yaml"), config=config)
