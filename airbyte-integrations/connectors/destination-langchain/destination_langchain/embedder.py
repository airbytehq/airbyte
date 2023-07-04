from abc import ABC, abstractmethod
from typing import Optional
from destination_langchain.config import EmbeddingConfigModel
from langchain.embeddings.base import Embeddings
from langchain.embeddings.openai import OpenAIEmbeddings

class Embedder(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        pass

    @property
    @abstractmethod
    def langchain_embeddings(self) -> Embeddings:
        pass

    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        pass

class OpenAIEmbedder(Embedder):
    def __init__(self, config: EmbeddingConfigModel):
        super().__init__()
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.openai_key, chunk_size=8191)
    
    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return str(e)
        return None
    
    @property
    def langchain_embeddings(self) -> Embeddings:
        return self.embeddings

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by text-embedding-ada-002 model
        return 1536
