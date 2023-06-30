from abc import ABC, abstractmethod
from destination_langchain.config import DocArrayHnswSearchIndexingModel, PineconeIndexingModel
from destination_langchain.embedder import Embedder
from destination_langchain.measure_time import measure_time
from destination_langchain.processor import METADATA_NATURAL_ID_FIELD, METADATA_STREAM_FIELD
from langchain.document_loaders.base import Document
from typing import Any, List, Optional, Tuple
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Type, Level, ConfiguredAirbyteCatalog, Status, AirbyteRecordMessage, AirbyteLogMessage
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
    def index(self, document_chunks: List[Document], document_ids: List[str], delete_ids: List[str]):
        pass

    @abstractmethod
    def check(self) -> Optional[str]: 
        pass

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

    def index(self, document_chunks, document_ids, delete_ids):
        for id in delete_ids:
            self.pinecone_index.delete(filter={METADATA_NATURAL_ID_FIELD: id})
        embedding_vectors = self.embed_fn([chunk.page_content for chunk in document_chunks])
        pinecone_docs = []
        for i in range(len(document_chunks)):
            chunk = document_chunks[i]
            metadata = chunk.metadata
            metadata["text"] = chunk.page_content
            pinecone_docs.append((document_ids[i], embedding_vectors[i], metadata))
        self.pinecone_index.upsert(vectors=pinecone_docs)
    
    def check(self) -> Optional[str]:
        try:
            pinecone.describe_index(self.config.index)
        except Exception as e:
            return str(e)
        return None


class DocArrayHnswSearchIndexer(Indexer):
    config: DocArrayHnswSearchIndexingModel
    def __init__(self, config: DocArrayHnswSearchIndexingModel, embedder: Embedder):
        super().__init__(config, embedder)
        self.vectorstore = DocArrayHnswSearch.from_params(self.embedder.langchain_embeddings, config.destination_path, 1536)

    def _create_directory_recursively(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            return f"Creation of the directory {path} failed, with error: {str(e)}"
        else:
            return None

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        for stream in catalog.streams:
            if stream.destination_sync_mode != "overwrite":
                raise Exception("DocArrayHnswSearchIndexer only supports overwrite mode")
        for file in os.listdir(self.config.destination_path):
            os.remove(os.path.join(self.config.destination_path, file))
    
    def index(self, document_chunks):
        self.vectorstore.add_documents(document_chunks)
    
    def check(self) -> Optional[str]:
        return self._create_directory_recursively(self.config.destination_path)