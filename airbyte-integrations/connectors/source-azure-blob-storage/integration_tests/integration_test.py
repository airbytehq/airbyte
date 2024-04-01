# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from source_azure_blob_storage import Config, SourceAzureBlobStorage, SourceAzureBlobStorageStreamReader


@pytest.mark.parametrize(
    "config",
    [
        "config_csv",
        "config_jsonl",
    ],
)
def test_read_jsonl_files(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any], request):
    """Read about 300Mb of raw csv files
    Test 3 streams: 2 * 1_000_000 recs + 1 * 1000 recs
    """
    config = request.getfixturevalue(config)
    source = SourceAzureBlobStorage(
        SourceAzureBlobStorageStreamReader(),
        spec_class=Config,
        catalog=configured_catalog,
        config=config,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == 300
