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
    astra_db_endpoint: str = Field(
        ...,
        title="AstraDB Endpoint",
        description="AstraDB Endpoint",
        pattern="^https:\/\/([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}-(af|il|ap|ca|eu|me|sa|us|cn|us-gov|us-iso|us-isob)-(central|north|(north(?:east|west))|south|south(?:east|west)|east|west)([0-9]{1})\\.apps\\.astra\\.datastax\\.com",
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
