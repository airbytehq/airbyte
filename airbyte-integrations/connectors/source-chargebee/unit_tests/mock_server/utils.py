# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder


def _get_manifest_path() -> Path:
    """Get path to manifest.yaml, handling both CI and local environments."""
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source(config: Mapping[str, Any], state=None) -> YamlDeclarativeSource:
    """Create a YamlDeclarativeSource instance with the given config."""
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def config() -> ConfigBuilder:
    return ConfigBuilder()


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """Read records from a single stream."""
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    return read(get_source(config=_config), _config, _catalog, state, expecting_exception)
