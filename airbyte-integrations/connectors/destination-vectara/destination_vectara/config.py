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


class OAuth2(BaseModel):
    client_id: str = Field(..., title="Client ID", description="OAuth2.0 client id", order=0)
    client_secret: str = Field(
        ..., title="Client Secret", description="OAuth2.0 client secret", airbyte_secret=True, order=1
    )

    class Config:
        title = "OAuth2.0 Credentials"
        schema_extra = {"description": "OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)"}

class VectaraIndexingConfigModel(BaseModel):
    oauth2: OAuth2 = Field(
        ..., title="OAuth2.0 Credentials", description="OAuth2.0 credentials used to authenticate admin actions (creating/deleting corpora)", type="object", order=1
    )
    customer_id: str = Field(..., title="Customer ID", description="Your customer id as it is in the authenticaion url", order=2)
    corpus_name: str = Field(..., title="Corpus Name", description="The Name of Corpus to load data into", order=2)
    # corpus_id: Optional[int] = Field(default="", title="Corpus ID", description="The ID of Corpus to load data into", order=3)

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
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")
    indexing: VectaraIndexingConfigModel

    class Config:
        title = "Vectara Destination Config"
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
