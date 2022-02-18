#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from collections import UserDict
from pathlib import Path
from typing import Iterable, List, Union

import pytest
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode
from source_acceptance_test.config import Config


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


def find_key_inside_schema(schema_item: Union[dict, list, str], key: str = "$ref") -> dict:
    """Checking the incoming schema for the presence of a `$ref` object in it"""
    if isinstance(schema_item, list):
        for list_schema_item in schema_item:
            item = find_key_inside_schema(list_schema_item, key)
            if item is not None:
                return item
    elif isinstance(schema_item, dict):
        if key in schema_item:
            return schema_item
        for schema_object_value in schema_item.values():
            item = find_key_inside_schema(schema_object_value, key)
            if item is not None:
                return item


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
