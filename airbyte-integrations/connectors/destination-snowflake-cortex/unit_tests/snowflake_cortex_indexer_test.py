#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest
import urllib3
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer
from airbyte_cdk.models import (
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
)

@pytest.fixture(scope="module")
def mock_processor():
    with patch("airbyte._processors.sql.snowflake.SnowflakeSqlProcessor") as mock:
        yield mock

def _create_snowflake_cortex_indexer(mock_processor):
    config = SnowflakeCortexIndexingModel(account="account", username="username", password="password", database="database", warehouse="warehouse", role="role")
    indexer = SnowflakeCortexIndexer(config, 3, Mock(ConfiguredAirbyteCatalog))
    # TODO: figure why mockprocessor is not getting mocked
    return indexer 
    


def _test_get_airbyte_messsages_from_chunks(mock_processor):
    indexer = _create_snowflake_cortex_indexer(mock_processor)
    indexer._get_airbyte_messsages_from_chunks(
        [
            Mock(page_content="test", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[1, 2, 3], 
                 record=AirbyteRecordMessage(namespace=None, stream='mystream', data={'str_col': 'Dogs are number 0', 'int_col': 0}, emitted_at=0)),
            Mock(page_content="test2", 
                 metadata={"_ab_stream": "abc"}, 
                 embedding=[4, 5, 6], 
                 record=AirbyteRecordMessage(namespace=None, stream='mystream', data={'str_col': 'Dogs are number 0', 'int_col': 0}, emitted_at=0))
        ],
    )
    pass 

    





