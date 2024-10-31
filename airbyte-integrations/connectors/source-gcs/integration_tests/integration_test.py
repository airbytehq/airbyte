# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
import os

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import read
from source_gcs import Config, SourceGCS, SourceGCSStreamReader

from .utils import load_config


def get_configured_catalog(file_format: str) -> ConfiguredAirbyteCatalog:
    return SourceGCS.read_catalog(f"{os.path.dirname(__file__)}/configured_catalogs/configured_catalog_{file_format}.json")


@pytest.mark.parametrize(
    "file_format, expected_num_of_records",
    [
        ("csv", 4),
        ("jsonl", 50),
        ("parquet", 366),
        ("avro", 5),
    ],
)
def test_read_files(file_format: str, expected_num_of_records: int):
    """Read records from bucket and assert number of records"""
    config = load_config(f"config_integration_{file_format}.json")
    configured_catalog = get_configured_catalog(file_format)
    source = SourceGCS(
        SourceGCSStreamReader(),
        spec_class=Config,
        catalog=configured_catalog,
        config=config,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == expected_num_of_records
