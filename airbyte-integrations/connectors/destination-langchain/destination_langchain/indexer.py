#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import os
import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import pinecone
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.models.airbyte_protocol import AirbyteLogMessage, AirbyteMessage, DestinationSyncMode, Level, Type
from destination_langchain.config import DocArrayHnswSearchIndexingModel, PineconeIndexingModel
from destination_langchain.document_processor import METADATA_RECORD_ID_FIELD, METADATA_STREAM_FIELD
from destination_langchain.embedder import Embedder
from destination_langchain.measure_time import measure_time
from destination_langchain.utils import format_exception
from langchain.document_loaders.base import Document
from langchain.vectorstores.docarray import DocArrayHnswSearch


class Indexer(ABC):
    def __init__(self, config: Any, embedder: Embedder):
        self.config = config
        self.embedder = embedder
        pass

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        pass

    def post_sync(self) -> List[AirbyteMessage]:
        pass

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

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.pinecone_index.delete(filter={METADATA_STREAM_FIELD: stream.stream.name})

    def post_sync(self):
        return [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.WARN, message=self.embed_fn._get_stats()))]

    def index(self, document_chunks, delete_ids):
        if len(delete_ids) > 0:
            self.pinecone_index.delete(filter={METADATA_RECORD_ID_FIELD: {"$in": delete_ids}})
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
            pinecone.describe_index(self.config.index)
        except Exception as e:
            return format_exception(e)
        return None

    @property
    def max_metadata_size(self) -> int:
        # leave some space for the text field
        return 40_960 - 10_000


class DocArrayHnswSearchIndexer(Indexer):
    config: DocArrayHnswSearchIndexingModel

    def __init__(self, config: DocArrayHnswSearchIndexingModel, embedder: Embedder):
        super().__init__(config, embedder)

    def _init_vectorstore(self):
        self.vectorstore = DocArrayHnswSearch.from_params(
            embedding=self.embedder.langchain_embeddings, work_dir=self.config.destination_path, n_dim=self.embedder.embedding_dimensions
        )

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        for stream in catalog.streams:
            if stream.destination_sync_mode != DestinationSyncMode.overwrite:
                raise Exception(
                    f"DocArrayHnswSearchIndexer only supports overwrite mode, got {stream.destination_sync_mode} for stream {stream.stream.name}"
                )
        for file in os.listdir(self.config.destination_path):
            os.remove(os.path.join(self.config.destination_path, file))
        self._init_vectorstore()

    def post_sync(self):
        return [AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.WARN, message=self.index._get_stats()))]

    @measure_time
    def index(self, document_chunks, delete_ids: List[str]):
        # does not support deleting documents, always full refresh sync
        self.vectorstore.add_documents(document_chunks)

    def check(self) -> Optional[str]:
        try:
            self._init_vectorstore()
        except Exception as e:
            return format_exception(e)
        return None
