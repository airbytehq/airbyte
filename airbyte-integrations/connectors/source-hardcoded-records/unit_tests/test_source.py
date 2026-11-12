# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path

from source_hardcoded_records.source import SourceHardcodedRecords

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


SAMPLE_CONFIG = json.loads((Path(__file__).parents[1] / "integration_tests" / "sample_config.json").read_text())


def test_check_connection():
    assert SourceHardcodedRecords().check_connection(logging.getLogger(__name__), SAMPLE_CONFIG) == (True, None)


def test_stream_names():
    source = SourceHardcodedRecords()

    assert [stream.name for stream in source.streams(SAMPLE_CONFIG)] == ["products", "customers", "dummy_fields"]


def test_read_records_from_each_stream():
    source = SourceHardcodedRecords()

    for stream in source.streams(SAMPLE_CONFIG):
        catalog = CatalogBuilder().with_stream(stream.name, SyncMode.full_refresh).build()
        output = read(source, SAMPLE_CONFIG, catalog)

        assert output.records, f"No records read from {stream.name}"
        assert output.errors == [], output.get_formatted_error_message()
