# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from source_azure_blob_storage import Config, SourceAzureBlobStorage, SourceAzureBlobStorageStreamReader


def test_read_csv_files(configured_catalog: ConfiguredAirbyteCatalog, config_csv: Mapping[str, Any]):
    """Read about 300Mb of raw csv files
    Test 3 streams: 2 * 1_000_000 recs + 1 * 1000 recs
    """
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=Config,
        catalog=configured_catalog,
        config=config_csv,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config_csv, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == 2_001_000


def test_read_jsonl_files(configured_catalog: ConfiguredAirbyteCatalog, config_jsonl: Mapping[str, Any]):
    """Read about 300Mb of raw csv files
    Test 3 streams: 2 * 1_000_000 recs + 1 * 1000 recs
    """
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=Config,
        catalog=configured_catalog,
        config=config_jsonl,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config_jsonl, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == 2_001_000
