#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock, Mock, call, patch

import pytest
import urllib3
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_snowflake_cortex.config import SnowflakeCortexIndexingModel
from destination_snowflake_cortex.indexer import SnowflakeCortexIndexer

def create_snowflake_cortex_indexer():
    config = SnowflakeCortexIndexingModel(mode="pinecone", pinecone_environment="myenv", pinecone_key="mykey", index="myindex")
    indexer = SnowflakeCortexIndexer(config, 3)
    return indexer


def snowflake_cortex_indexer_test():
    pass 



def generate_catalog():
    return ConfiguredAirbyteCatalog.parse_obj(
        {
            "streams": [
                {
                    "stream": {
                        "name": "example_stream",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                        "namespace": "ns1",
                    },
                    "primary_key": [["id"]],
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append_dedup",
                },
                {
                    "stream": {
                        "name": "example_stream2",
                        "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["column_name"],
                        "namespace": "ns2",
                    },
                    "primary_key": [["id"]],
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                },
            ]
        }
    )






