#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union, cast

from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.utils import create_chunks, format_exception
from airbyte_cdk.models import AirbyteRecordMessage
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.embeddings.fake import FakeEmbeddings
from langchain.embeddings.localai import LocalAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings


@dataclass
class Document:
    page_content: str
    record: AirbyteRecordMessage


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
    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
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

OPEN_AI_TOKEN_LIMIT = 150_000  # limit of tokens per minute


class BaseOpenAIEmbedder(Embedder):
    def __init__(self, embeddings: OpenAIEmbeddings, chunk_size: int):
        super().__init__()
        self.embeddings = embeddings
        self.chunk_size = chunk_size

    def check(self) -> Optional[str]:
        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        """
        Embed the text of each chunk and return the resulting embedding vectors.

        As the OpenAI API will fail if more than the per-minute limit worth of tokens is sent at once, we split the request into batches and embed each batch separately.
        It's still possible to run into the rate limit between each embed call because the available token budget hasn't recovered between the calls,
        but the built-in retry mechanism of the OpenAI client handles that.
        """
        # Each chunk can hold at most self.chunk_size tokens, so tokens-per-minute by maximum tokens per chunk is the number of documents that can be embedded at once without exhausting the limit in a single request
        embedding_batch_size = OPEN_AI_TOKEN_LIMIT // self.chunk_size
        batches = create_chunks(documents, batch_size=embedding_batch_size)
        embeddings: List[Optional[List[float]]] = []
        for batch in batches:
            embeddings.extend(self.embeddings.embed_documents([chunk.page_content for chunk in batch]))
        return embeddings

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by text-embedding-ada-002 model
        return OPEN_AI_VECTOR_SIZE


class OpenAIEmbedder(BaseOpenAIEmbedder):
    def __init__(self, config: OpenAIEmbeddingConfigModel, chunk_size: int):
        super().__init__(OpenAIEmbeddings(openai_api_key=config.openai_key, max_retries=15, disallowed_special=()), chunk_size)  # type: ignore


class AzureOpenAIEmbedder(BaseOpenAIEmbedder):
    def __init__(self, config: AzureOpenAIEmbeddingConfigModel, chunk_size: int):
        # Azure OpenAI API has — as of 20230927 — a limit of 16 documents per request
        super().__init__(OpenAIEmbeddings(openai_api_key=config.openai_key, chunk_size=16, max_retries=15, openai_api_type="azure", openai_api_version="2023-05-15", openai_api_base=config.api_base, deployment=config.deployment, disallowed_special=()), chunk_size)  # type: ignore


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

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        return cast(List[Optional[List[float]]], self.embeddings.embed_documents([document.page_content for document in documents]))

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

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        return cast(List[Optional[List[float]]], self.embeddings.embed_documents([document.page_content for document in documents]))

    @property
    def embedding_dimensions(self) -> int:
        # use same vector size as for OpenAI embeddings to keep it realistic
        return OPEN_AI_VECTOR_SIZE


CLOUD_DEPLOYMENT_MODE = "cloud"


class OpenAICompatibleEmbedder(Embedder):
    def __init__(self, config: OpenAICompatibleEmbeddingConfigModel):
        super().__init__()
        self.config = config
        # Client is set internally
        # Always set an API key even if there is none defined in the config because the validator will fail otherwise. Embedding APIs that don't require an API key don't fail if one is provided, so this is not breaking usage.
        self.embeddings = LocalAIEmbeddings(model=config.model_name, openai_api_key=config.api_key or "dummy-api-key", openai_api_base=config.base_url, max_retries=15, disallowed_special=())  # type: ignore

    def check(self) -> Optional[str]:
        deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
        if deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE and not self.config.base_url.startswith("https://"):
            return "Base URL must start with https://"

        try:
            self.embeddings.embed_query("test")
        except Exception as e:
            return format_exception(e)
        return None

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        return cast(List[Optional[List[float]]], self.embeddings.embed_documents([document.page_content for document in documents]))

    @property
    def embedding_dimensions(self) -> int:
        # vector size produced by the model
        return self.config.dimensions


class FromFieldEmbedder(Embedder):
    def __init__(self, config: FromFieldEmbeddingConfigModel):
        super().__init__()
        self.config = config

    def check(self) -> Optional[str]:
        return None

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        """
        From each chunk, pull the embedding from the field specified in the config.
        Check that the field exists, is a list of numbers and is the correct size. If not, raise an AirbyteTracedException explaining the problem.
        """
        embeddings: List[Optional[List[float]]] = []
        for document in documents:
            data = document.record.data
            if self.config.field_name not in data:
                raise AirbyteTracedException(
                    internal_message="Embedding vector field not found",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}... in stream {document.record.stream}  does not contain embedding vector field {self.config.field_name}. Please check your embedding configuration, the embedding vector field has to be set correctly on every record.",
                )
            field = data[self.config.field_name]
            if not isinstance(field, list) or not all(isinstance(x, (int, float)) for x in field):
                raise AirbyteTracedException(
                    internal_message="Embedding vector field not a list of numbers",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}...  in stream {document.record.stream} does contain embedding vector field {self.config.field_name}, but it is not a list of numbers. Please check your embedding configuration, the embedding vector field has to be a list of numbers of length {self.config.dimensions} on every record.",
                )
            if len(field) != self.config.dimensions:
                raise AirbyteTracedException(
                    internal_message="Embedding vector field has wrong length",
                    failure_type=FailureType.config_error,
                    message=f"Record {str(data)[:250]}...  in stream {document.record.stream} does contain embedding vector field {self.config.field_name}, but it has length {len(field)} instead of the configured {self.config.dimensions}. Please check your embedding configuration, the embedding vector field has to be a list of numbers of length {self.config.dimensions} on every record.",
                )
            embeddings.append(field)

        return embeddings

    @property
    def embedding_dimensions(self) -> int:
        return self.config.dimensions


embedder_map = {
    "openai": OpenAIEmbedder,
    "cohere": CohereEmbedder,
    "fake": FakeEmbedder,
    "azure_openai": AzureOpenAIEmbedder,
    "from_field": FromFieldEmbedder,
    "openai_compatible": OpenAICompatibleEmbedder,
}


def create_from_config(
    embedding_config: Union[
        AzureOpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        OpenAIEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ],
    processing_config: ProcessingConfigModel,
) -> Embedder:

    if embedding_config.mode == "azure_openai" or embedding_config.mode == "openai":
        return cast(Embedder, embedder_map[embedding_config.mode](embedding_config, processing_config.chunk_size))
    else:
        return cast(Embedder, embedder_map[embedding_config.mode](embedding_config))
