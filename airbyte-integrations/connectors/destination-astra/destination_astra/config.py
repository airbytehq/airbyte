#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field


class AstraIndexingModel(BaseModel):
    astra_db_app_token: str = Field(
        ...,
        title="AstraDB Application Token",
        airbyte_secret=True,
        description="AstraDB Application Token",
    )
    astra_db_id: str = Field(
        ...,
        title="AstraDB Id",
        airbyte_secret=True,
        description="AstraDB Id",
    )
    astra_db_region: str = Field(
        ...,
        title="AstraDB Region",
        description="AstraDB Region",
        examples=["us-east1"],
    )
    astra_db_keyspace: str = Field(
        ..., 
        title="AstraDB Keyspace", 
        description="Astra DB Keyspace"
        )
    collection: str = Field(
        ...,
        title="AstraDB collection",
        description="AstraDB collection"
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Astra DB gives developers the APIs, real-time data and ecosystem integrations to put accurate RAG and Gen AI apps with fewer hallucinations in production.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: AstraIndexingModel
