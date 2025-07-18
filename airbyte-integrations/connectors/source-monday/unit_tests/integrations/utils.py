# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import operator
from pathlib import Path
from typing import Any, Dict, List, Optional

from airbyte_cdk.models import AirbyteMessage, SyncMode
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path / "manifest.yaml"
    return Path(__file__).parent.parent.parent / "manifest.yaml"


_YAML_FILE_PATH = _get_manifest_path()
print(f"Using YAML file path: {_YAML_FILE_PATH}")


def read_stream(
    stream_name: str, sync_mode: SyncMode, config: Dict[str, Any], state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        YamlDeclarativeSource(config=config, catalog=catalog, state=state, path_to_yaml=_YAML_FILE_PATH),
        config,
        catalog,
        state,
        expecting_exception,
    )


def get_log_messages_by_log_level(logs: List[AirbyteMessage], log_level: LogLevel) -> List[str]:
    return map(operator.attrgetter("log.message"), filter(lambda x: x.log.level == log_level, logs))
