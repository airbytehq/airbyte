#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from unittest.mock import PropertyMock

import jsonschema
import pytest
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from source_file.source import SourceFile

logger = logging.getLogger("airbyte")


@pytest.fixture
def source():
    return SourceFile()


@pytest.fixture
def config():
    config_path: str = "integration_tests/config.json"
    with open(config_path, "r") as f:
        return json.loads(f.read())


def test_csv_with_utf16_encoding(absolute_path, test_files):
    config_local_csv_utf16 = {
        "dataset_name": "AAA",
        "format": "csv",
        "reader_options": '{"encoding":"utf_16"}',
        "url": f"{absolute_path}/{test_files}/test_utf16.csv",
        "provider": {"storage": "local"},
    }
    expected_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "properties": {
            "header1": {"type": ["string", "null"]},
            "header2": {"type": ["number", "null"]},
            "header3": {"type": ["number", "null"]},
            "header4": {"type": ["boolean", "null"]},
        },
        "type": "object",
    }

    catalog = SourceFile().discover(logger=logger, config=config_local_csv_utf16)
    stream = next(iter(catalog.streams))
    assert stream.json_schema == expected_schema


def get_catalog(properties):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="test",
                    json_schema={"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": properties},
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


def test_nan_to_null(absolute_path, test_files):
    """make sure numpy.nan converted to None"""
    config = {
        "dataset_name": "test",
        "format": "csv",
        "reader_options": json.dumps({"sep": ";"}),
        "url": f"{absolute_path}/{test_files}/test_nan.csv",
        "provider": {"storage": "local"},
    }

    catalog = get_catalog(
        {"col1": {"type": ["string", "null"]}, "col2": {"type": ["number", "null"]}, "col3": {"type": ["number", "null"]}}
    )

    source = SourceFile()
    records = source.read(logger=logger, config=config, catalog=catalog)
    records = [r.record.data for r in records]
    assert records == [
        {"col1": "key1", "col2": 1.11, "col3": None},
        {"col1": "key2", "col2": None, "col3": 2.22},
        {"col1": "key3", "col2": None, "col3": None},
        {"col1": "key4", "col2": 3.33, "col3": None},
    ]

    config.update({"format": "yaml", "url": f"{absolute_path}/{test_files}/formats/yaml/demo.yaml"})
    records = source.read(logger=logger, config=config, catalog=catalog)
    records = [r.record.data for r in records]
    assert records == []

    config.update({"provider": {"storage": "SSH", "user": "user", "host": "host"}})

    with pytest.raises(Exception):
        next(source.read(logger=logger, config=config, catalog=catalog))


def test_spec(source):
    spec = source.spec(None)
    assert isinstance(spec, ConnectorSpecification)


def test_check(source, config):
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    actual = source.check(logger=logger, config=config)
    assert actual == expected


def test_check_invalid_config(source, invalid_config):
    expected = AirbyteConnectionStatus(status=Status.FAILED)
    actual = source.check(logger=logger, config=invalid_config)
    assert actual.status == expected.status


def test_discover(source, config, client):
    catalog = source.discover(logger=logger, config=config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)

    type(client).streams = PropertyMock(side_effect=Exception)

    with pytest.raises(Exception):
        source.discover(logger=logger, config=config)
