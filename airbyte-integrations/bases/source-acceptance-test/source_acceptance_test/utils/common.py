#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from collections import UserDict
from pathlib import Path
from typing import Iterable, List, MutableMapping, Set, Union

import pytest
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from source_acceptance_test.config import Config, EmptyStreamConfiguration


def load_config(path: str) -> Config:
    """Function to load test config, avoid duplication of code in places where we can't use fixture"""
    path = Path(path) / "acceptance-test-config.yml"
    if not path.exists():
        pytest.fail(f"config file {path.absolute()} does not exist")

    with open(str(path), "r") as file:
        data = load(file, Loader=Loader)
        return Config.parse_obj(data)


def full_refresh_only_catalog(configured_catalog: ConfiguredAirbyteCatalog) -> ConfiguredAirbyteCatalog:
    """Transform provided catalog to catalog with all streams configured to use Full Refresh sync (when possible)"""
    streams = []
    for stream in configured_catalog.streams:
        if SyncMode.full_refresh in stream.stream.supported_sync_modes:
            stream.sync_mode = SyncMode.full_refresh
            streams.append(stream)

    configured_catalog.streams = streams
    return configured_catalog


def incremental_only_catalog(configured_catalog: ConfiguredAirbyteCatalog) -> ConfiguredAirbyteCatalog:
    """Transform provided catalog to catalog with all streams configured to use Incremental sync (when possible)"""
    streams = []
    for stream in configured_catalog.streams:
        if SyncMode.incremental in stream.stream.supported_sync_modes:
            stream.sync_mode = SyncMode.incremental
            streams.append(stream)

    configured_catalog.streams = streams
    return configured_catalog


def filter_output(records: Iterable[AirbyteMessage], type_) -> List[AirbyteMessage]:
    """Filter messages to match specific type"""
    return list(filter(lambda x: x.type == type_, records))


class SecretDict(UserDict):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(******)"

    def __repr__(self) -> str:
        return str(self)


def find_keyword_schema(schema: Union[dict, list, str], key: str) -> bool:
    """Find at least one keyword in a schema, skip object properties"""

    def _find_keyword(schema, key, _skip=False):
        if isinstance(schema, list):
            for v in schema:
                _find_keyword(v, key)
        elif isinstance(schema, dict):
            for k, v in schema.items():
                if k == key and not _skip:
                    raise StopIteration
                rec_skip = k == "properties" and schema.get("type") == "object"
                _find_keyword(v, key, rec_skip)

    try:
        _find_keyword(schema, key)
    except StopIteration:
        return True
    return False


def load_yaml_or_json_path(path: Path):
    with open(str(path), "r") as file:
        file_data = file.read()
        file_ext = path.suffix
        if file_ext == ".json":
            return json.loads(file_data)
        elif file_ext == ".yaml":
            return load(file_data, Loader=Loader)
        else:
            raise RuntimeError("path must be a '.yaml' or '.json' file")


def find_all_values_for_key_in_schema(schema: dict, searched_key: str):
    """Retrieve all (nested) values in a schema for a specific searched key"""
    if isinstance(schema, list):
        for schema_item in schema:
            yield from find_all_values_for_key_in_schema(schema_item, searched_key)
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == searched_key:
                yield value
            if isinstance(value, dict) or isinstance(value, list):
                yield from find_all_values_for_key_in_schema(value, searched_key)


def build_configured_catalog_from_discovered_catalog_and_empty_streams(
    discovered_catalog: MutableMapping[str, AirbyteStream], empty_streams: Set[EmptyStreamConfiguration]
):
    """Build a configured catalog from the discovered catalog with empty streams removed.

    Args:
        discovered_catalog (MutableMapping[str, AirbyteStream]): The discovered catalog.
        empty_streams (Set[EmptyStreamConfiguration]): The set of empty streams declared in the test configuration.

    Returns:
        ConfiguredAirbyteCatalog: a configured Airbyte catalog.
    """
    empty_stream_names = [empty_stream.name for empty_stream in empty_streams]
    streams = [
        ConfiguredAirbyteStream(
            stream=stream,
            sync_mode=stream.supported_sync_modes[0],
            destination_sync_mode=DestinationSyncMode.append,
            cursor_field=stream.default_cursor_field,
            primary_key=stream.source_defined_primary_key,
        )
        for _, stream in discovered_catalog.items()
        if stream.name not in empty_stream_names
    ]
    if empty_stream_names:
        logging.warning(
            f"The configured catalog was built with the discovered catalog from which the following empty streams were removed: {', '.join(empty_stream_names)}."
        )
    else:
        logging.info("The configured catalog is built from a fully discovered catalog.")
    return ConfiguredAirbyteCatalog(streams=streams)


def build_configured_catalog_from_custom_catalog(configured_catalog_path: str, discovered_catalog: MutableMapping[str, AirbyteStream]):
    """Build a configured catalog from a local one stored in a JSON file.

    Args:
        configured_catalog_path (str): Local path to a custom configured catalog path
        discovered_catalog (MutableMapping[str, AirbyteStream]): The discovered catalog

    Returns:
        ConfiguredAirbyteCatalog: a configured Airbyte catalog
    """
    catalog = ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)
    for configured_stream in catalog.streams:
        try:
            configured_stream.stream = discovered_catalog[configured_stream.stream.name]
        except KeyError:
            pytest.fail(
                f"The {configured_stream.stream.name} stream you have set in {configured_catalog_path} is not part of the discovered_catalog"
            )
    logging.info("The configured catalog is built from a custom configured catalog.")
    return catalog
