#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.utils.spec_schema_transformations import resolve_refs
from pydantic import BaseModel, Field


class PineconeIndexingModel(BaseModel):
    pinecone_key: str = Field(..., title="Pinecone API key", airbyte_secret=True)
    pinecone_environment: str = Field(..., title="Pinecone environment", description="Pinecone environment to use")
    index: str = Field(..., title="Index", description="Pinecone index to use")

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Pinecone is a popular vector store that can be used to store and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(BaseModel):
    indexing: PineconeIndexingModel

    embedding: Union[OpenAIEmbeddingConfigModel, CohereEmbeddingConfigModel, FakeEmbeddingConfigModel] = Field(
        ..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object"
    )
    processing: ProcessingConfigModel

    class Config:
        title = "Pinecone Destination Config"
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

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema
