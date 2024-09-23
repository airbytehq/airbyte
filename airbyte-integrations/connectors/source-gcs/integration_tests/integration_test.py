# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.file_based.stream.cursor import DefaultFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from source_gcs import SourceGCS, Config, SourceGCSStreamReader


@pytest.mark.parametrize(
    "config",
    [
        "config_csv",
        # "config_jsonl",
        # "config_parquet",
        # "config_avro",
    ],
)
def test_read_files(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any], request):
    """Read records"""
    config = request.getfixturevalue(config)
    source = SourceGCS(
        SourceGCSStreamReader(),
        spec_class=Config,
        catalog=configured_catalog,
        config=config,
        state=None,
        cursor_cls=DefaultFileBasedCursor,
    )
    output = read(source=source, config=config, catalog=configured_catalog)
    assert sum(x.state.sourceStats.recordCount for x in output.state_messages) == 2


