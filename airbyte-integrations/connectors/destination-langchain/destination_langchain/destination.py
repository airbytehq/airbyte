#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    Status,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from destination_langchain.batcher import Batcher
from destination_langchain.config import ConfigModel
from destination_langchain.document_processor import DocumentProcessor
from destination_langchain.embedder import Embedder, FakeEmbedder, OpenAIEmbedder
from destination_langchain.indexer import DocArrayHnswSearchIndexer, Indexer, PineconeIndexer
from langchain.document_loaders.base import Document

BATCH_SIZE = 128

indexer_map = {"pinecone": PineconeIndexer, "DocArrayHnswSearch": DocArrayHnswSearchIndexer}

embedder_map = {"openai": OpenAIEmbedder, "fake": FakeEmbedder}


class DestinationLangchain(Destination):
    indexer: Indexer
    processor: DocumentProcessor
    embedder: Embedder

    def _init_indexer(self, config: ConfigModel):
        self.embedder = embedder_map[config.embedding.mode](config.embedding)
        self.indexer = indexer_map[config.indexing.mode](config.indexing, self.embedder)

    def _process_batch(self, batch: List[AirbyteRecordMessage]):
        documents: List[Document] = []
        ids_to_delete = []
        for record in batch:
            record_documents, record_id_to_delete = self.processor.process(record)
            documents.extend(record_documents)
            if record_id_to_delete is not None:
                ids_to_delete.append(record_id_to_delete)
        self.indexer.index(documents, ids_to_delete)

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        config_model = ConfigModel.parse_obj(config)
        self._init_indexer(config_model)
        self.processor = DocumentProcessor(config_model.processing, configured_catalog, max_metadata_size=self.indexer.max_metadata_size)
        batcher = Batcher(BATCH_SIZE, lambda batch: self._process_batch(batch))
        self.indexer.pre_sync(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                batcher.flush()
                yield message
            elif message.type == Type.RECORD:
                batcher.add(message.record)
        batcher.flush()
        yield from self.indexer.post_sync()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        self._init_indexer(ConfigModel.parse_obj(config))
        embedder_error = self.embedder.check()
        indexer_error = self.indexer.check()
        errors = [error for error in [embedder_error, indexer_error] if error is not None]
        if len(errors) > 0:
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
