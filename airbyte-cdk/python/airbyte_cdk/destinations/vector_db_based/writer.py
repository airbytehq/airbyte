#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk, DocumentProcessor
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder
from airbyte_cdk.destinations.vector_db_based.indexer import Indexer
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type


class Writer:
    """
    The Writer class is orchestrating the document processor, the embedder and the indexer:
    * Incoming records are passed through the document processor to generate documents
    * One the configured batch size is reached, the documents are passed to the embedder to generate embeddings
    * The embedder embeds the documents
    * The indexer deletes old documents by the associated record id before indexing the new ones

    The destination connector is responsible to create a writer instance and pass the input messages iterable to the write method.
    The batch size can be configured by the destination connector to give the freedom of either letting the user configure it or hardcoding it to a sensible value depending on the destination.
    The omit_raw_text parameter can be used to omit the raw text from the documents. This can be useful if the raw text is very large and not needed for the destination.
    """

    def __init__(
        self, processing_config: ProcessingConfigModel, indexer: Indexer, embedder: Embedder, batch_size: int, omit_raw_text: bool
    ) -> None:
        self.processing_config = processing_config
        self.indexer = indexer
        self.embedder = embedder
        self.batch_size = batch_size
        self.omit_raw_text = omit_raw_text
        self._init_batch()

    def _init_batch(self) -> None:
        self.documents: Dict[Tuple[str, str], List[Chunk]] = defaultdict(list)
        self.ids_to_delete: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        self.number_of_documents = 0

    def _process_batch(self) -> None:
        for (namespace, stream), ids in self.ids_to_delete.items():
            self.indexer.delete(ids, namespace, stream)

        for (namespace, stream), documents in self.documents.items():
            embeddings = self.embedder.embed_chunks(documents)
            for i, document in enumerate(documents):
                document.embedding = embeddings[i]
                if self.omit_raw_text:
                    document.page_content = None
            self.indexer.index(documents, namespace, stream)

        self._init_batch()

    def write(self, configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
        self.processor = DocumentProcessor(self.processing_config, configured_catalog)
        self.indexer.pre_sync(configured_catalog)
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                self._process_batch()
                yield message
            elif message.type == Type.RECORD:
                record_documents, record_id_to_delete = self.processor.process(message.record)
                self.documents[(message.record.namespace, message.record.stream)].extend(record_documents)
                if record_id_to_delete is not None:
                    self.ids_to_delete[(message.record.namespace, message.record.stream)].append(record_id_to_delete)
                self.number_of_documents += len(record_documents)
                if self.number_of_documents >= self.batch_size:
                    self._process_batch()

        self._process_batch()
        yield from self.indexer.post_sync()
