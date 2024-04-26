#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field


class AstraIndexingModel(BaseModel):
    astra_db_app_token: str = Field(
        ...,
        title="Astra DB Application Token",
        airbyte_secret=True,
        description="The application token authorizes a user to connect to a specific Astra DB database. It is created when the user clicks the Generate Token button on the Overview tab of the Database page in the Astra UI.",
    )
    astra_db_endpoint: str = Field(
        ...,
        title="Astra DB Endpoint",
        description="The endpoint specifies which Astra DB database queries are sent to. It can be copied from the Database Details section of the Overview tab of the Database page in the Astra UI.",
        pattern="^https:\\/\\/([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}-[^\\.]*?\\.apps\\.astra\\.datastax\\.com",
        examples=["https://8292d414-dd1b-4c33-8431-e838bedc04f7-us-east1.apps.astra.datastax.com"],
    )
    astra_db_keyspace: str = Field(
        ...,
        title="Astra DB Keyspace",
        description="Keyspaces (or Namespaces) serve as containers for organizing data within a database. You can create a new keyspace uisng the Data Explorer tab in the Astra UI. The keyspace default_keyspace is created for you when you create a Vector Database in Astra DB.",
    )
    collection: str = Field(
        ...,
        title="Astra DB collection",
        description="Collections hold data. They are analagous to tables in traditional Cassandra terminology. This tool will create the collection with the provided name automatically if it does not already exist. Alternatively, you can create one thorugh the Data Explorer tab in the Astra UI.",
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Astra DB gives developers the APIs, real-time data and ecosystem integrations to put accurate RAG and Gen AI apps with fewer hallucinations in production.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: AstraIndexingModel
