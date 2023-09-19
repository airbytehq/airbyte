#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ProcessingConfigModel(BaseModel):
    chunk_size: int = Field(
        ...,
        title="Chunk size",
        maximum=8191,
        description="Size of chunks in tokens to store in vector store (make sure it is not too big for the context if your LLM)",
    )
    chunk_overlap: int = Field(
        title="Chunk overlap",
        description="Size of overlap between chunks in tokens to store in vector store to better capture relevant context",
        default=0,
    )
    text_fields: Optional[List[str]] = Field(
        default=[],
        title="Text fields to embed",
        description="List of fields in the record that should be used to calculate the embedding. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered text fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.",
        always_show=True,
        examples=["text", "user.name", "users.*.name"],
    )
    metadata_fields: Optional[List[str]] = Field(
        default=[],
        title="Fields to store as metadata",
        description="List of fields in the record that should be stored as metadata. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered metadata fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array. When specifying nested paths, all matching values are flattened into an array set to a field named by the path.",
        always_show=True,
        examples=["age", "user", "user.name"],
    )

    class Config:
        schema_extra = {"group": "processing"}


class OpenAIEmbeddingConfigModel(BaseModel):
    mode: Literal["openai"] = Field("openai", const=True)
    openai_key: str = Field(..., title="OpenAI API key", airbyte_secret=True)

    class Config:
        title = "OpenAI"
        schema_extra = {
            "description": "Use the OpenAI API to embed text. This option is using the text-embedding-ada-002 model with 1536 embedding dimensions."
        }


class AzureOpenAIEmbeddingConfigModel(BaseModel):
    mode: Literal["azure_openai"] = Field("azure_openai", const=True)
    openai_key: str = Field(
        ...,
        title="Azure OpenAI API key",
        airbyte_secret=True,
        description="The API key for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
    )
    api_base: str = Field(
        ...,
        title="Resource base URL",
        description="The base URL for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
        examples=["https://your-resource-name.openai.azure.com"],
    )
    deployment: str = Field(
        ...,
        title="Deployment",
        description="The deployment for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
        examples=["your-resource-name"],
    )

    class Config:
        title = "Azure OpenAI"
        schema_extra = {
            "description": "Use the Azure-hosted OpenAI API to embed text. This option is using the text-embedding-ada-002 model with 1536 embedding dimensions."
        }


class FakeEmbeddingConfigModel(BaseModel):
    mode: Literal["fake"] = Field("fake", const=True)

    class Config:
        title = "Fake"
        schema_extra = {
            "description": "Use a fake embedding made out of random vectors with 1536 embedding dimensions. This is useful for testing the data pipeline without incurring any costs."
        }


class FromFieldEmbeddingConfigModel(BaseModel):
    mode: Literal["from_field"] = Field("from_field", const=True)
    field_name: str = Field(
        ..., title="Field name", description="Name of the field in the record that contains the embedding", examples=["embedding", "vector"]
    )
    dimensions: int = Field(
        ..., title="Embedding dimensions", description="The number of dimensions the embedding model is generating", examples=[1536, 384]
    )

    class Config:
        title = "From Field"
        schema_extra = {
            "description": "Use a field in the record as the embedding. This is useful if you already have an embedding for your data and want to store it in the vector store."
        }


class CohereEmbeddingConfigModel(BaseModel):
    mode: Literal["cohere"] = Field("cohere", const=True)
    cohere_key: str = Field(..., title="Cohere API key", airbyte_secret=True)

    class Config:
        title = "Cohere"
        schema_extra = {"description": "Use the Cohere API to embed text."}
