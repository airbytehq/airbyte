#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Literal, Optional, Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig
from airbyte_cdk.utils.spec_schema_transformations import resolve_refs
from pydantic import BaseModel, Field


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Milvus instance", order=1)
    password: str = Field(..., title="Password", description="Password for the Milvus instance", airbyte_secret=True, order=2)

    class Config(OneOfOptionConfig):
        title = "Username/Password"
        description = "Authenticate using username and password (suitable for self-managed Milvus clusters)"
        discriminator = "mode"


class NoAuth(BaseModel):
    mode: Literal["no_auth"] = Field("no_auth", const=True)

    class Config(OneOfOptionConfig):
        title = "No auth"
        description = "Do not authenticate (suitable for locally running test clusters, do not use for clusters with public IP addresses)"
        discriminator = "mode"


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)
    token: str = Field(..., title="API Token", description="API Token for the Milvus instance", airbyte_secret=True)

    class Config(OneOfOptionConfig):
        title = "API Token"
        description = "Authenticate using an API token (suitable for Zilliz Cloud)"
        discriminator = "mode"


class MilvusIndexingConfigModel(BaseModel):
    host: str = Field(
        ...,
        title="Public Endpoint",
        order=1,
        description="The public endpoint of the Milvus instance. ",
        examples=["https://my-instance.zone.zillizcloud.com", "tcp://host.docker.internal:19530", "tcp://my-local-milvus:19530"],
    )
    db: Optional[str] = Field(title="Database Name", description="The database to connect to", default="")
    collection: str = Field(..., title="Collection Name", description="The collection to load data into", order=3)
    auth: Union[TokenAuth, UsernamePasswordAuth, NoAuth] = Field(
        ..., title="Authentication", description="Authentication method", discriminator="mode", type="object", order=2
    )
    vector_field: str = Field(title="Vector Field", description="The field in the entity that contains the vector", default="vector")
    text_field: str = Field(title="Text Field", description="The field in the entity that contains the embedded text", default="text")

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        AzureOpenAIEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")
    indexing: MilvusIndexingConfigModel

    class Config:
        title = "Milvus Destination Config"
        schema_extra = {
            "groups": [
                {"id": "processing", "title": "Processing"},
                {"id": "embedding", "title": "Embedding"},
                {"id": "indexing", "title": "Indexing"},
            ]
        }

    @staticmethod
    def remove_discriminator(schema: dict) -> None:
        """pydantic adds "discriminator" to the schema for oneOfs, which is not treated right by the platform as we inline all references"""
        dpath.util.delete(schema, "properties/*/discriminator")
        dpath.util.delete(schema, "properties/**/discriminator")

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema
