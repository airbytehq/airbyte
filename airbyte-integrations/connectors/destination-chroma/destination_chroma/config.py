#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Literal, Optional, Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.utils.spec_schema_transformations import resolve_refs
from pydantic import BaseModel, Field


class HttpMode(BaseModel):
    mode: Literal["http_client"] = Field("http_client", const=True)
    host: str = Field(..., title="Host", description="The URL to the chromadb instance", order=0)
    port: int = Field(..., title="Port", description="The port to the chromadb instance", order=1)
    ssl: bool = Field(..., title="SSL", description="Whether to use SSL to connect to the Chroma server", order=2)
    username: Optional[str] = Field(default="", title="Username", description="Username used in server/client mode only", order=3)
    password: Optional[str] = Field(
        default="", title="Password", description="Password used in server/client mode only", airbyte_secret=True, order=4
    )

    class Config:
        title = "Client/Server Mode"
        schema_extra = {"description": "Authenticate using username and password (suitable for self-managed Chroma clusters)"}


class PersistentMode(BaseModel):
    mode: Literal["persistent_client"] = Field("persistent_client", const=True)
    path: str = Field(..., title="Path", description="Where Chroma will store its database files on disk, and load them on start.")

    class Config:
        title = "Persistent Client Mode"
        schema_extra = {"description": "Configure Chroma to save and load from your local machine"}


class ChromaIndexingConfigModel(BaseModel):

    auth_method: Union[PersistentMode, HttpMode] = Field(
        ..., title="Connection Mode", description="Mode how to connect to Chroma", discriminator="mode", type="object", order=0
    )
    collection_name: str = Field(..., title="Collection Name", description="The collection to load data into", order=3)

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }


class NoEmbeddingConfigModel(BaseModel):
    mode: Literal["no_embedding"] = Field("no_embedding", const=True)

    class Config:
        title = "Chroma Default Embedding Function"
        schema_extra = {
            "description": "Do not calculate embeddings. Chromadb uses the sentence transfomer (https://www.sbert.net/index.html) as a default if an embedding function is not defined. Note that depending on your hardware, calculating embeddings locally can be very slow and is mostly suited for prototypes."
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        NoEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")
    indexing: ChromaIndexingConfigModel

    class Config:
        title = "Chroma Destination Config"
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
