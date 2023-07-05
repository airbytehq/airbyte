from abc import ABC, abstractmethod
import uuid
from destination_langchain.config import DocArrayHnswSearchIndexingModel, PineconeIndexingModel
from destination_langchain.embedder import Embedder
from destination_langchain.measure_time import measure_time
from destination_langchain.document_processor import METADATA_NATURAL_ID_FIELD, METADATA_STREAM_FIELD
from langchain.document_loaders.base import Document
from typing import Any, List, Optional, Tuple
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    Type,
    Level,
    ConfiguredAirbyteCatalog,
    Status,
    AirbyteRecordMessage,
    AirbyteLogMessage,
)
from langchain.vectorstores.docarray import DocArrayHnswSearch
from langchain.vectorstores import Pinecone
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
import os
import pinecone


class Indexer(ABC):
    def __init__(self, config: Any, embedder: Embedder):
        self.config = config
        self.embedder = embedder
        pass

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        pass

    def post_sync(self):
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


class PineconeIndexer(Indexer):
    config: PineconeIndexingModel

    def __init__(self, config: PineconeIndexingModel, embedder: Embedder):
        super().__init__(config, embedder)
        pinecone.init(api_key=config.pinecone_key, environment=config.pinecone_environment)
        self.pinecone_index = pinecone.Index(config.index)
        self.embed_fn = measure_time(self.embedder.langchain_embeddings.embed_documents)

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        for stream in catalog.streams:
            if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                self.pinecone_index.delete(filter={METADATA_STREAM_FIELD: stream.stream.name})

    def post_sync(self):
        self.embed_fn._print_stats()

    def index(self, document_chunks, delete_ids):
        if len(delete_ids) > 0:
            self.pinecone_index.delete(filter={METADATA_NATURAL_ID_FIELD: {"$in": delete_ids}})
        embedding_vectors = self.embed_fn([chunk.page_content for chunk in document_chunks])
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            pinecone_docs.append((str(uuid.uuid4()), embedding_vectors[i], metadata))
        self.pinecone_index.upsert(vectors=pinecone_docs)

    def check(self) -> Optional[str]:
        try:
            pinecone.describe_index(self.config.index)
        except Exception as e:
            return str(e)
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
                raise Exception(f"DocArrayHnswSearchIndexer only supports overwrite mode, got {stream.destination_sync_mode} for stream {stream.stream.name}")
        for file in os.listdir(self.config.destination_path):
            os.remove(os.path.join(self.config.destination_path, file))
        self._init_vectorstore()

    def post_sync(self):
        self.index._print_stats()

    @measure_time
    def index(self, document_chunks, delete_ids: List[str]):
        # does not support deleting documents, always full refresh sync
        self.vectorstore.add_documents(document_chunks)

    def check(self) -> Optional[str]:
        try:
            self._init_vectorstore()
        except Exception as e:
            return str(e)
        return None
