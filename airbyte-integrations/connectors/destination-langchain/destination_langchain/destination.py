#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping, List, Dict, Optional
import random
import json
import os
from destination_langchain.batcher import Batcher
from destination_langchain.embedder import Embedder, OpenAIEmbedder
from destination_langchain.indexer import DocArrayHnswSearchIndexer, Indexer, PineconeIndexer
from destination_langchain.processor import Processor
from destination_langchain.config import ConfigModel
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode

import dpath.util
from dpath.exceptions import PathNotFound
import pinecone
import jsonref
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Type, Level, ConfiguredAirbyteCatalog, Status, AirbyteRecordMessage, AirbyteLogMessage
from langchain.utils import stringify_dict
from langchain.document_loaders.base import BaseLoader, Document
from langchain.vectorstores.docarray import DocArrayHnswSearch
from langchain.vectorstores import Pinecone
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

BATCH_SIZE = 10

indexer_map = {
    "pinecone": PineconeIndexer,
    "DocArrayHnswSearch": DocArrayHnswSearchIndexer
}

class DestinationLangchain(Destination):
    indexer: Indexer
    processor: Processor
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = OpenAIEmbedder(config.embedding)
        self.indexer = indexer_map[config.indexing.mode](config.indexing, self.embedder)

    def _process_batch(self, batch: List[AirbyteRecordMessage]):
        documents = []
        document_ids = []
        ids_to_delete = []
        for record in batch:
            record_documents, record_document_ids, record_ids_to_delete = self.processor.process(record)
            documents.extend(record_documents)
            document_ids.extend(record_document_ids)
            ids_to_delete.extend(record_ids_to_delete)
        self.indexer.index(documents, document_ids, ids_to_delete)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self.processor = Processor(config_model.processing, configured_catalog)
        self._init_indexer(config_model)
        batcher = Batcher(BATCH_SIZE, lambda batch: self._process_batch(batch))
        self.indexer.pre_sync(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                batcher.flush()
                yield message
            if message.type == Type.RECORD:
                batcher.add(message.record)
                batcher.flush_if_necessary()
            else:
                continue
        batcher.flush()
        self.indexer.post_sync()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._init_indexer(ConfigModel.parse_obj(config))
        embedder_error = self.embedder.check()
        indexer_error = self.indexer.check()
        if embedder_error is not None or indexer_error is not None:
            errors = [error for error in [embedder_error, indexer_error] if error is not None]
            return AirbyteConnectionStatus(status=Status.FAILED, message="\n".join(errors))
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        
    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/langchain",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
