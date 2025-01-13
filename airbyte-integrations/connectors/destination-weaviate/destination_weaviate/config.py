#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Literal, Union

from pydantic import BaseModel, Field

from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    VectorDBConfigModel,
)
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Weaviate cluster", order=1)
    password: str = Field(..., title="Password", description="Password for the Weaviate cluster", airbyte_secret=True, order=2)

    class Config(OneOfOptionConfig):
        title = "Username/Password"
        description = "Authenticate using username and password (suitable for self-managed Weaviate clusters)"
        discriminator = "mode"


class NoAuth(BaseModel):
    mode: Literal["no_auth"] = Field("no_auth", const=True)

    class Config(OneOfOptionConfig):
        title = "No Authentication"
        description = "Do not authenticate (suitable for locally running test clusters, do not use for clusters with public IP addresses)"
        discriminator = "mode"


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)
    token: str = Field(..., title="API Token", description="API Token for the Weaviate instance", airbyte_secret=True)

    class Config(OneOfOptionConfig):
        title = "API Token"
        description = "Authenticate using an API token (suitable for Weaviate Cloud)"
        discriminator = "mode"


class Header(BaseModel):
    header_key: str = Field(..., title="Header Key")
    value: str = Field(..., title="Header Value", airbyte_secret=True)


class WeaviateIndexingConfigModel(BaseModel):
    host: str = Field(
        ...,
        title="Public Endpoint",
        order=1,
        description="The public endpoint of the Weaviate cluster.",
        examples=["https://my-cluster.weaviate.network"],
    )
    auth: Union[TokenAuth, UsernamePasswordAuth, NoAuth] = Field(
        ..., title="Authentication", description="Authentication method", discriminator="mode", type="object", order=2
    )
    batch_size: int = Field(title="Batch Size", description="The number of records to send to Weaviate in each batch", default=128)
    text_field: str = Field(title="Text Field", description="The field in the object that contains the embedded text", default="text")
    tenant_id: str = Field(title="Tenant ID", description="The tenant ID to use for multi tenancy", airbyte_secret=True, default="")
    default_vectorizer: str = Field(
        title="Default Vectorizer",
        description="The vectorizer to use if new classes need to be created",
        default="none",
        enum=[
            "none",
            "text2vec-cohere",
            "text2vec-huggingface",
            "text2vec-openai",
            "text2vec-palm",
            "text2vec-contextionary",
            "text2vec-transformers",
            "text2vec-gpt4all",
        ],
    )
    additional_headers: List[Header] = Field(
        title="Additional headers",
        description="Additional HTTP headers to send with every request.",
        default=[],
        examples=[{"header_key": "X-OpenAI-Api-Key", "value": "my-openai-api-key"}],
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }


class NoEmbeddingConfigModel(BaseModel):
    mode: Literal["no_embedding"] = Field("no_embedding", const=True)

    class Config(OneOfOptionConfig):
        title = "No external embedding"
        description = "Do not calculate and pass embeddings to Weaviate. Suitable for clusters with configured vectorizers to calculate embeddings within Weaviate or for classes that should only support regular text search."
        discriminator = "mode"


class ConfigModel(VectorDBConfigModel):
    indexing: WeaviateIndexingConfigModel
    embedding: Union[
        NoEmbeddingConfigModel,
        AzureOpenAIEmbeddingConfigModel,
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")
