#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import pinecone
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteLogMessage,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    Level,
    Type,
)
from destination_pinecone.config import PineconeIndexingModel
from destination_pinecone.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from destination_pinecone.embedder import Embedder
from destination_pinecone.measure_time import measure_time
from destination_pinecone.utils import format_exception
from langchain.schema import Document


class Indexer(ABC):
    def __init__(self, config: Any, embedder: Embedder):
        self.config = config
        self.embedder = embedder
        pass

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        pass

    def post_sync(self) -> List[AirbyteMessage]:
        return []

    @abstractmethod
    def index(self, document_chunks: List[Document], delete_ids: List[str]):
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        pass

    @property
    def max_metadata_size(self) -> Optional[int]:
        return None


def chunks(iterable, batch_size):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


# large enough to speed up processing, small enough to not hit pinecone request limits
PINECONE_BATCH_SIZE = 40


class PineconeIndexer(Indexer):
    config: PineconeIndexingModel

    def __init__(self, config: PineconeIndexingModel, embedder: Embedder):
        super().__init__(config, embedder)
        pinecone.init(api_key=config.pinecone_key, environment=config.pinecone_environment, threaded=True)

        self.pinecone_index = pinecone.Index(config.index, pool_threads=10)
        self.embed_fn = measure_time(self.embedder.langchain_embeddings.embed_documents)
        self.embedding_dimensions = embedder.embedding_dimensions

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        index_description = pinecone.describe_index(self.config.index)
        self._pod_type = index_description.pod_type
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.delete_vectors(filter={METADATA_STREAM_FIELD: stream.stream.name})

    def post_sync(self):
        return [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.WARN, message=self.embed_fn._get_stats()))]

    def delete_vectors(self, filter):
        if self._pod_type == "starter":
            # Starter pod types have a maximum of 100000 rows
            top_k = 10000
            self.delete_by_metadata(filter, top_k)
        else:
            self.pinecone_index.delete(filter=filter)

    def delete_by_metadata(self, filter, top_k):
        zero_vector = [0.0] * self.embedding_dimensions
        query_result = self.pinecone_index.query(vector=zero_vector, filter=filter, top_k=top_k)
        vector_ids = [doc.id for doc in query_result.matches]
        if len(vector_ids) > 0:
            self.pinecone_index.delete(ids=vector_ids)

    def index(self, document_chunks, delete_ids):
        if len(delete_ids) > 0:
            self.delete_vectors(filter={METADATA_RECORD_ID_FIELD: {"$in": delete_ids}})
        embedding_vectors = self.embed_fn([chunk.page_content for chunk in document_chunks])
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            pinecone_docs.append((str(uuid.uuid4()), embedding_vectors[i], metadata))
        async_results = [
            self.pinecone_index.upsert(vectors=ids_vectors_chunk, async_req=True, show_progress=False)
            for ids_vectors_chunk in chunks(pinecone_docs, batch_size=PINECONE_BATCH_SIZE)
        ]
        # Wait for and retrieve responses (this raises in case of error)
        [async_result.get() for async_result in async_results]

    def check(self) -> Optional[str]:
        try:
            description = pinecone.describe_index(self.config.index)
            actual_dimension = int(description.dimension)
            if actual_dimension != self.embedder.embedding_dimensions:
                return f"Your embedding configuration will produce vectors with dimension {self.embedder.embedding_dimensions:d}, but your index is configured with dimension {actual_dimension:d}. Make sure embedding and indexing configurations match."
        except Exception as e:
            return format_exception(e)
        return None

    @property
    def max_metadata_size(self) -> int:
        # leave some space for the text field
        return 40_960 - 10_000
