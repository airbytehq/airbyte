#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.destinations.vector_db_based.utils import format_exception
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.embeddings.fake import FakeEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


class Embedder(ABC):
    """
    Embedder is an abstract class that defines the interface for embedding text.

    The Indexer class uses the Embedder class to internally embed text - each indexer is responsible to pass the text of all documents to the embedder and store the resulting embeddings in the destination.
    The destination connector is responsible to create an embedder instance and pass it to the writer.
    The CDK defines basic embedders that should be supported in each destination. It is possible to implement custom embedders for special destinations if needed.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def check(self) -> Optional[str]:
        pass

    @abstractmethod
    def embed_chunks(self, chunks: List[Chunk]) -> List[Optional[List[float]]]:
        """
        Embed the text of each chunk and return the resulting embedding vectors.
        If a chunk cannot be embedded or is configured to not be embedded, return None for that chunk.
        """
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
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.openai_key, chunk_size=8191, max_retries=15)  # type: ignore

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        return self.embeddings.embed_documents([chunk.page_content for chunk in chunks])

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

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        return self.embeddings.embed_documents([chunk.page_content for chunk in chunks])

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

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        return self.embeddings.embed_documents([chunk.page_content for chunk in chunks])

    @property
    def embedding_dimensions(self) -> int:
        # use same vector size as for OpenAI embeddings to keep it realistic
        return OPEN_AI_VECTOR_SIZE


class FromFieldEmbedder(Embedder):
    def __init__(self, config: FromFieldEmbeddingConfigModel):
        super().__init__()
        self.config = config

    def check(self) -> Optional[str]:
        return None

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """
        From each chunk, pull the embedding from the field specified in the config.
        Check that the field exists, is a list of numbers and is the correct size. If not, raise an AirbyteTracedException explaining the problem.
        """
        embeddings = []
        for chunk in chunks:
            data = chunk.record.data
            if self.config.field_name not in data:
                raise AirbyteTracedException(
                    internal_message="Embedding vector field not found",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}... in stream {chunk.record.stream}  does not contain embedding vector field {self.config.field_name}. Please check your embedding configuration, the embedding vector field has to be set correctly on every record.",
                )
            field = data[self.config.field_name]
            if not isinstance(field, list) or not all(isinstance(x, (int, float)) for x in field):
                raise AirbyteTracedException(
                    internal_message="Embedding vector field not a list of numbers",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}...  in stream {chunk.record.stream} does contain embedding vector field {self.config.field_name}, but it is not a list of numbers. Please check your embedding configuration, the embedding vector field has to be a list of numbers of length {self.config.dimensions} on every record.",
                )
            if len(field) != self.config.dimensions:
                raise AirbyteTracedException(
                    internal_message="Embedding vector field has wrong length",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}...  in stream {chunk.record.stream} does contain embedding vector field {self.config.field_name}, but it has length {len(field)} instead of the configured {self.config.dimensions}. Please check your embedding configuration, the embedding vector field has to be a list of numbers of length {self.config.dimensions} on every record.",
                )
            embeddings.append(field)

        return embeddings

    @property
    def embedding_dimensions(self) -> int:
        return self.config.dimensions
