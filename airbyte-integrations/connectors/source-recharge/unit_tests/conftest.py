# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def get_source(
    config: Mapping[str, Any],
    catalog: Optional[ConfiguredAirbyteCatalog] = None,
    state: Optional[List[AirbyteStateMessage]] = None,
) -> YamlDeclarativeSource:
    manifest_folder = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_folder.exists():
        manifest_folder = Path(__file__).parent.parent
    return YamlDeclarativeSource(path_to_yaml=str(manifest_folder / "manifest.yaml"), config=config, catalog=catalog, state=state)
