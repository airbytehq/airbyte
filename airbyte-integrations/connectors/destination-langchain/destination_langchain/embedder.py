#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional

from destination_langchain.config import FakeEmbeddingConfigModel, OpenAIEmbeddingConfigModel
from destination_langchain.utils import format_exception
from langchain.embeddings.base import Embeddings
from langchain.embeddings.fake import FakeEmbeddings
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


OPEN_AI_VECTOR_SIZE = 1536


class OpenAIEmbedder(Embedder):
    def __init__(self, config: OpenAIEmbeddingConfigModel):
        super().__init__()
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.openai_key, chunk_size=8191)

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    @property
    def langchain_embeddings(self) -> Embeddings:
        return self.embeddings

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by text-embedding-ada-002 model
        return OPEN_AI_VECTOR_SIZE


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

    @property
    def langchain_embeddings(self) -> Embeddings:
        return self.embeddings

    @property
    def embedding_dimensions(self) -> int:
        # use same vector size as for OpenAI embeddings to keep it realistic
        return OPEN_AI_VECTOR_SIZE
