# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import os
import sys
from pathlib import Path

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

ENV_REQUEST_CACHE_PATH = "REQUEST_CACHE_PATH"
os.environ["REQUEST_CACHE_PATH"] = ENV_REQUEST_CACHE_PATH


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def find_stream(stream_name, config):
    for stream in YamlDeclarativeSource(config=config, catalog=None, state=None, path_to_yaml=str(_YAML_FILE_PATH)).streams(config=config):
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def delete_cache_files(cache_directory):
    directory_path = Path(cache_directory)
    if directory_path.exists() and directory_path.is_dir():
        for file_path in directory_path.glob("*.sqlite"):
            file_path.unlink()


@fixture(autouse=True)
def clear_cache_before_each_test():
    # The problem: Once the first request is cached, we will keep getting the cached result no matter what setup we prepared for a particular test.
    # Solution: We must delete the cache before each test because for the same URL, we want to define multiple responses and status codes.
    delete_cache_files(os.getenv(ENV_REQUEST_CACHE_PATH))
    yield
