# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from source_azure_blob_storage import SourceAzureBlobStorage, SourceAzureBlobStorageSpec, SourceAzureBlobStorageStreamReader


@pytest.mark.parametrize(
    "config",
    [
        "config_csv",
        "config_jsonl",
        "config_parquet",
        "config_avro",
    ],
)
def test_read_files(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any], request):
    """Read 2_001_000 records in 30 files"""
    config = request.getfixturevalue(config)
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=SourceAzureBlobStorageSpec,
        catalog=configured_catalog,
        config=config,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == 2_001_000
