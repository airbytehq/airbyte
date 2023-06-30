from abc import ABC, abstractmethod
from destination_langchain.embedder import Embedder
from langchain.document_loaders.base import Document
from typing import List, Optional, Tuple
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Type, Level, ConfiguredAirbyteCatalog, Status, AirbyteRecordMessage, AirbyteLogMessage
from langchain.vectorstores.docarray import DocArrayHnswSearch
from langchain.vectorstores import Pinecone
import os
import pinecone

class Indexer(ABC):
    def __init__(self, config: dict, embedder: Embedder):
        self.config = config
        self.embedder = embedder
        pass

    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        pass
    
    @abstractmethod
    def index(self, document_chunks: List[Document], document_ids: List[str], delete_ids: List[str]):
        pass

    @abstractmethod
    def check(self) -> Optional[str]: 
        pass

class PineconeIndexer(Indexer):
    def __init__(self, config: dict, embedder: Embedder):
        super().__init__(config, embedder)
        pinecone.init(api_key=config.get("pinecone_key"), environment=config.get("pinecone_environment"))
        self.pinecone_index = pinecone.Index(config.get("index"))
        self.vectorstore = Pinecone(self.index, self.embedder.langchain_embeddings.embed_query, "text")
    
    def pre_sync(self, catalog: ConfiguredAirbyteCatalog):
        for stream in catalog.streams:
            if stream.destination_sync_mode == "overwrite":
                self.pinecone_index.delete(filter={"_airbyte_stream": stream.stream.name})
    
    def index(self, document_chunks, document_ids, delete_ids):
        for id in delete_ids:
            self.pinecone_index.delete(filter={"_natural_id": id})
        self.vectorstore.add_documents(document_chunks, ids=document_ids)
    
    def check(self) -> Optional[str]:
        try:
            pinecone.describe_index(self.config.get("index"))
        except Exception as e:
            return str(e)
        return None


class DocArrayHnswSearchIndexer(Indexer):
    def __init__(self, config: dict, embedder: Embedder):
        super().__init__(config, embedder)
        self.vectorstore = DocArrayHnswSearch.from_params(self.embedder.langchain_embeddings, config.get("destination_path"), 1536)

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
        for file in os.listdir(self.config.get("destination_path")):
            os.remove(os.path.join(self.config.get("destination_path"), file))
    
    def index(self, document_chunks):
        self.vectorstore.add_documents(document_chunks)
    
    def check(self) -> Optional[str]:
        return self._create_directory_recursively(self.config.get("destination_path"))