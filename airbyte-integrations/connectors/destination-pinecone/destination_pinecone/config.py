#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.destinations.vector_db_based.config import VectorDBConfigModel
from pydantic import BaseModel, Field


class PineconeIndexingModel(BaseModel):
    pinecone_key: str = Field(
        ...,
        title="Pinecone API key",
        airbyte_secret=True,
        description="The Pinecone API key to use matching the environment (copy from Pinecone console)",
    )
    pinecone_environment: str = Field(
        ..., title="Pinecone Environment", description="Pinecone Cloud environment to use", examples=["us-west1-gcp", "gcp-starter"]
    )
    index: str = Field(..., title="Index", description="Pinecone index in your project to load data into")
    namespace: str = Field(
        ...,
        title="Default Namespace",
        description='The default namespace tables are written to if the source does not specify a namespace. See more <a href="https://docs.pinecone.io/guides/indexes/use-namespaces">here</a>.',
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "description": "Pinecone is a popular vector store that can be used to store and retrieve embeddings.",
            "group": "indexing",
        }


class ConfigModel(VectorDBConfigModel):
    indexing: PineconeIndexingModel
