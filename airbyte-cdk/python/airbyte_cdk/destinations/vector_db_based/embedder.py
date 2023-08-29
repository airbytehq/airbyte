#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.config import CohereEmbeddingConfigModel, FakeEmbeddingConfigModel, OpenAIEmbeddingConfigModel
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.embeddings.fake import FakeEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


class Embedder(ABC):
    """
    Embedder is an abstract class that defines the interface for embedding text.

    The Indexer class uses the Embedder class to internally embed text - each indexer is responsible to pass the text of all documents to the embedder and store the resulting embeddings in the destination.
    The destination connector is responsible to create an embedder instance and pass it to the indexer.
    The CDK defines basic embedders that should be supported in each destination. It is possible to implement custom embedders for special destinations if needed.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        pass


OPEN_AI_VECTOR_SIZE = 1536


class OpenAIEmbedder(Embedder):
    def __init__(self, config: OpenAIEmbeddingConfigModel):
        super().__init__()
        # Client is set internally
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.openai_key, chunk_size=8191)  # type: ignore

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by text-embedding-ada-002 model
        return OPEN_AI_VECTOR_SIZE


COHERE_VECTOR_SIZE = 1024


class CohereEmbedder(Embedder):
    def __init__(self, config: CohereEmbeddingConfigModel):
        super().__init__()
        # Client is set internally
        self.embeddings = CohereEmbeddings(cohere_api_key=config.cohere_key, model="embed-english-light-v2.0")  # type: ignore

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by text-embedding-ada-002 model
        return COHERE_VECTOR_SIZE


class FakeEmbedder(Embedder):
    def __init__(self, config: FakeEmbeddingConfigModel):
        super().__init__()
        self.embeddings = FakeEmbeddings(size=OPEN_AI_VECTOR_SIZE)

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    @property
    def embedding_dimensions(self) -> int:
        # use same vector size as for OpenAI embeddings to keep it realistic
        return OPEN_AI_VECTOR_SIZE
