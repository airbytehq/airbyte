#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_protocol_dataclasses.models import ConfiguredAirbyteCatalog
from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


@fixture(autouse=True)
def clear_cache_before_each_test():
    """Clear the HTTP request cache before each test to prevent test pollution."""
    cache_path = os.environ.get("REQUEST_CACHE_PATH")
    if cache_path and os.path.exists(cache_path):
        import shutil

        shutil.rmtree(cache_path, ignore_errors=True)


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def get_source(config, catalog: Optional[ConfiguredAirbyteCatalog] = None, state=None) -> YamlDeclarativeSource:
    catalog = catalog or CatalogBuilder().build()
    state = state if state is not None else StateBuilder().build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def find_stream(stream_name, config):
    streams = get_source(config).streams(config=config)

    # cache should be disabled once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513
    for stream in streams:
        stream._stream_partition_generator._partition_factory._retriever.requester.use_cache = True

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)


def load_json_file(file_name: str) -> Mapping[str, Any]:
    with open(f"{os.path.dirname(__file__)}/{file_name}", "r") as data:
        return json.load(data)
