#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from pathlib import Path

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from source_file.source import SourceFile

HERE = Path(__file__).parent.absolute()


def test_csv_with_utf16_encoding():

    config_local_csv_utf16 = {
        "dataset_name": "AAA",
        "format": "csv",
        "reader_options": '{"encoding":"utf_16"}',
        "url": f"{HERE}/../integration_tests/sample_files/test_utf16.csv",
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

    catalog = SourceFile().discover(logger=logging.getLogger("airbyte"), config=config_local_csv_utf16)
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


def test_nan_to_null():
    """make sure numpy.nan converted to None"""
    config = {
        "dataset_name": "test",
        "format": "csv",
        "reader_options": json.dumps({"sep": ";"}),
        "url": f"{HERE}/../integration_tests/sample_files/test_nan.csv",
        "provider": {"storage": "local"},
    }

    catalog = get_catalog(
        {
            "col1": {"type": ["string", "null"]},
            "col2": {"type": ["number", "null"]},
        }
    )

    source = SourceFile()
    records = source.read(logger=logging.getLogger("airbyte"), config=config, catalog=catalog)
    records = [r.record.data for r in records]
    assert records == [
        {"col1": "key1", "col2": 1.1},
        {"col1": "key2", "col2": None},
        {"col1": "key3", "col2": None},
        {"col1": "key4", "col2": 2.2},
    ]
