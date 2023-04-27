#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from copy import deepcopy
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
        "reader_options": '{"encoding":"utf_16", "parse_dates": [\"header5\"]}',
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
            "header5": {"type": ["string", "null"], "format": "datetime"},
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
                    supported_sync_modes=[SyncMode.full_refresh],
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
    records = source.read(logger=logger, config=deepcopy(config), catalog=catalog)
    records = [r.record.data for r in records]
    assert records == [
        {"col1": "key1", "col2": 1.11, "col3": None},
        {"col1": "key2", "col2": None, "col3": 2.22},
        {"col1": "key3", "col2": None, "col3": None},
        {"col1": "key4", "col2": 3.33, "col3": None},
    ]

    config.update({"format": "yaml", "url": f"{absolute_path}/{test_files}/formats/yaml/demo.yaml"})
    records = source.read(logger=logger, config=deepcopy(config), catalog=catalog)
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


def test_discover_dropbox_link(source, config_dropbox_link):
    source.discover(logger=logger, config=config_dropbox_link)


def test_discover(source, config, client):
    catalog = source.discover(logger=logger, config=config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)

    type(client).streams = PropertyMock(side_effect=Exception)

    with pytest.raises(Exception):
        source.discover(logger=logger, config=config)


def test_check_wrong_reader_options(source, config):
    config["reader_options"] = '{encoding":"utf_16"}'
    assert source.check(logger=logger, config=config) == AirbyteConnectionStatus(
        status=Status.FAILED, message="Field 'reader_options' is not valid JSON. https://www.json.org/"
    )


def test_check_google_spreadsheets_url(source, config):
    config["url"] = "https://docs.google.com/spreadsheets/d/"
    assert source.check(logger=logger, config=config) == AirbyteConnectionStatus(
        status=Status.FAILED,
        message="Failed to load https://docs.google.com/spreadsheets/d/: please use the Official Google Sheets Source connector",
    )


def test_pandas_header_not_none(absolute_path, test_files):
    config = {
        "dataset_name": "test",
        "format": "csv",
        "reader_options": json.dumps({}),
        "url": f"{absolute_path}/{test_files}/test_no_header.csv",
        "provider": {"storage": "local"},
    }

    catalog = get_catalog({"text11": {"type": ["string", "null"]}, "text12": {"type": ["string", "null"]}})

    source = SourceFile()
    records = source.read(logger=logger, config=deepcopy(config), catalog=catalog)
    records = [r.record.data for r in records]
    assert records == [
        {"text11": "text21", "text12": "text22"},
    ]


def test_pandas_header_none(absolute_path, test_files):
    config = {
        "dataset_name": "test",
        "format": "csv",
        "reader_options": json.dumps({"header": None}),
        "url": f"{absolute_path}/{test_files}/test_no_header.csv",
        "provider": {"storage": "local"},
    }

    catalog = get_catalog({"0": {"type": ["string", "null"]}, "1": {"type": ["string", "null"]}})

    source = SourceFile()
    records = source.read(logger=logger, config=deepcopy(config), catalog=catalog)
    records = [r.record.data for r in records]
    assert records == [
        {"0": "text11", "1": "text12"},
        {"0": "text21", "1": "text22"},
    ]
