#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Iterable, List

from airbyte_cdk.destinations.vector_db_based.batcher import Batcher
from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk, DocumentProcessor
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, Type


class Writer:
    """
    The Writer class is orchestrating the document processor, the batcher and the indexer:
    * Incoming records are collected using the batcher
    * The document processor generates documents from all records in the batch
    * The indexer indexes the resulting documents in the destination

    The destination connector is responsible to create a writer instance and pass the input messages iterable to the write method.
    The batch size can be configured by the destination connector to give the freedom of either letting the user configure it or hardcoding it to a sensible value depending on the destination.
    """

    def __init__(self, processing_config: ProcessingConfigModel, indexer: Indexer, batch_size: int) -> None:
        self.processing_config = processing_config
        self.indexer = indexer
        self.batcher = Batcher(batch_size, lambda batch: self._process_batch(batch))

    def _process_batch(self, batch: List[AirbyteRecordMessage]) -> None:
        documents: List[Chunk] = []
        ids_to_delete = []
        for record in batch:
            record_documents, record_id_to_delete = self.processor.process(record)
            documents.extend(record_documents)
            if record_id_to_delete is not None:
                ids_to_delete.append(record_id_to_delete)
        self.indexer.index(documents, ids_to_delete)

    def write(self, configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
        self.processor = DocumentProcessor(self.processing_config, configured_catalog)
        self.indexer.pre_sync(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                self.batcher.flush()
                yield message
            elif message.type == Type.RECORD:
                self.batcher.add(message.record)
        self.batcher.flush()
        yield from self.indexer.post_sync()
