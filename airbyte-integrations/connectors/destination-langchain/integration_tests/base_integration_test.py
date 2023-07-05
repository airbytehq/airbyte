#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
import tempfile
import time
from typing import Any, Dict, Mapping
import unittest
from destination_langchain.embedder import OPEN_AI_VECTOR_SIZE

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from destination_langchain.destination import DestinationLangchain
from langchain import OpenAI, PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayHnswSearch
from langchain.embeddings import FakeEmbeddings
import pinecone


class BaseIntegrationTest(unittest.TestCase):
    def _get_configured_catalog(self, destination_mode: DestinationSyncMode) -> ConfiguredAirbyteCatalog:
        stream_schema = {"type": "object", "properties": {"str_col": {"type": "str"}, "int_col": {"type": "integer"}}}

        overwrite_stream = ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="mystream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]
            ),
            primary_key=[["int_col"]],
            sync_mode=SyncMode.incremental,
            destination_sync_mode=destination_mode,
        )

        return ConfiguredAirbyteCatalog(streams=[overwrite_stream])

    def _state(self, data: Dict[str, Any]) -> AirbyteMessage:
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))

    def _record(self, stream: str, str_value: str, int_value: int) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
        )