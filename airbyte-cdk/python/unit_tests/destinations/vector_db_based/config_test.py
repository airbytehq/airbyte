#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    ProcessingConfigModel,
)
from airbyte_cdk.utils.spec_schema_transformations import resolve_refs
from pydantic import BaseModel, Field


class IndexingModel(BaseModel):
    foo: str = Field(
        ...,
        title="Foo",
        description="Foo",
    )


class ConfigModel(BaseModel):
    indexing: IndexingModel

    embedding: Union[
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        AzureOpenAIEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(
        ...,
        title="Embedding",
        description="Embedding configuration",
        discriminator="mode",
        group="embedding",
        type="object",
    )
    processing: ProcessingConfigModel

    class Config:
        title = "My Destination Config"
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
        dpath.util.delete(schema, "properties/**/discriminator")

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema


def test_json_schema_generation():
    # This is the expected output of the schema generation
    expected = {
        "title": "My Destination Config",
        "type": "object",
        "properties": {
            "indexing": {
                "title": "IndexingModel",
                "type": "object",
                "properties": {"foo": {"title": "Foo", "description": "Foo", "type": "string"}},
                "required": ["foo"],
            },
            "embedding": {
                "title": "Embedding",
                "description": "Embedding configuration",
                "group": "embedding",
                "type": "object",
                "oneOf": [
                    {
                        "title": "OpenAI",
                        "type": "object",
                        "properties": {
                            "mode": {
                                "title": "Mode",
                                "default": "openai",
                                "const": "openai",
                                "enum": ["openai"],
                                "type": "string",
                            },
                            "openai_key": {
                                "title": "OpenAI API key",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                        },
                        "required": ["openai_key", "mode"],
                        "description": "Use the OpenAI API to embed text. This option is using the text-embedding-ada-002 model with 1536 embedding dimensions.",
                    },
                    {
                        "title": "Cohere",
                        "type": "object",
                        "properties": {
                            "mode": {
                                "title": "Mode",
                                "default": "cohere",
                                "const": "cohere",
                                "enum": ["cohere"],
                                "type": "string",
                            },
                            "cohere_key": {
                                "title": "Cohere API key",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                        },
                        "required": ["cohere_key", "mode"],
                        "description": "Use the Cohere API to embed text.",
                    },
                    {
                        "title": "Fake",
                        "type": "object",
                        "properties": {
                            "mode": {
                                "title": "Mode",
                                "default": "fake",
                                "const": "fake",
                                "enum": ["fake"],
                                "type": "string",
                            }
                        },
                        "description": "Use a fake embedding made out of random vectors with 1536 embedding dimensions. This is useful for testing the data pipeline without incurring any costs.",
                        "required": ["mode"],
                    },
                    {
                        "title": "Azure OpenAI",
                        "type": "object",
                        "properties": {
                            "mode": {
                                "title": "Mode",
                                "default": "azure_openai",
                                "const": "azure_openai",
                                "enum": ["azure_openai"],
                                "type": "string",
                            },
                            "openai_key": {
                                "title": "Azure OpenAI API key",
                                "description": "The API key for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                            "api_base": {
                                "title": "Resource base URL",
                                "description": "The base URL for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
                                "examples": ["https://your-resource-name.openai.azure.com"],
                                "type": "string",
                            },
                            "deployment": {
                                "title": "Deployment",
                                "description": "The deployment for your Azure OpenAI resource.  You can find this in the Azure portal under your Azure OpenAI resource",
                                "examples": ["your-resource-name"],
                                "type": "string",
                            },
                        },
                        "required": ["openai_key", "api_base", "deployment", "mode"],
                        "description": "Use the Azure-hosted OpenAI API to embed text. This option is using the text-embedding-ada-002 model with 1536 embedding dimensions.",
                    },
                    {
                        "title": "OpenAI-compatible",
                        "type": "object",
                        "properties": {
                            "mode": {
                                "title": "Mode",
                                "default": "openai_compatible",
                                "const": "openai_compatible",
                                "enum": ["openai_compatible"],
                                "type": "string",
                            },
                            "api_key": {
                                "title": "API key",
                                "default": "",
                                "airbyte_secret": True,
                                "type": "string",
                            },
                            "base_url": {
                                "title": "Base URL",
                                "description": "The base URL for your OpenAI-compatible service",
                                "examples": ["https://your-service-name.com"],
                                "type": "string",
                            },
                            "model_name": {
                                "title": "Model name",
                                "description": "The name of the model to use for embedding",
                                "default": "text-embedding-ada-002",
                                "examples": ["text-embedding-ada-002"],
                                "type": "string",
                            },
                            "dimensions": {
                                "title": "Embedding dimensions",
                                "description": "The number of dimensions the embedding model is generating",
                                "examples": [1536, 384],
                                "type": "integer",
                            },
                        },
                        "required": ["base_url", "dimensions", "mode"],
                        "description": "Use a service that's compatible with the OpenAI API to embed text.",
                    },
                ],
            },
            "processing": {
                "title": "ProcessingConfigModel",
                "type": "object",
                "properties": {
                    "chunk_size": {
                        "title": "Chunk size",
                        "description": "Size of chunks in tokens to store in vector store (make sure it is not too big for the context if your LLM)",
                        "maximum": 8191,
                        "minimum": 1,
                        "type": "integer",
                    },
                    "chunk_overlap": {
                        "title": "Chunk overlap",
                        "description": "Size of overlap between chunks in tokens to store in vector store to better capture relevant context",
                        "default": 0,
                        "type": "integer",
                    },
                    "text_fields": {
                        "title": "Text fields to embed",
                        "description": "List of fields in the record that should be used to calculate the embedding. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered text fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.",
                        "default": [],
                        "always_show": True,
                        "examples": ["text", "user.name", "users.*.name"],
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "metadata_fields": {
                        "title": "Fields to store as metadata",
                        "description": "List of fields in the record that should be stored as metadata. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered metadata fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array. When specifying nested paths, all matching values are flattened into an array set to a field named by the path.",
                        "default": [],
                        "always_show": True,
                        "examples": ["age", "user", "user.name"],
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "text_splitter": {
                        "title": "Text splitter",
                        "description": "Split text fields into chunks based on the specified method.",
                        "type": "object",
                        "oneOf": [
                            {
                                "title": "By Separator",
                                "type": "object",
                                "properties": {
                                    "mode": {
                                        "title": "Mode",
                                        "default": "separator",
                                        "const": "separator",
                                        "enum": ["separator"],
                                        "type": "string",
                                    },
                                    "separators": {
                                        "title": "Separators",
                                        "description": 'List of separator strings to split text fields by. The separator itself needs to be wrapped in double quotes, e.g. to split by the dot character, use ".". To split by a newline, use "\\n".',
                                        "default": ['"\\n\\n"', '"\\n"', '" "', '""'],
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "keep_separator": {
                                        "title": "Keep separator",
                                        "description": "Whether to keep the separator in the resulting chunks",
                                        "default": False,
                                        "type": "boolean",
                                    },
                                },
                                "description": "Split the text by the list of separators until the chunk size is reached, using the earlier mentioned separators where possible. This is useful for splitting text fields by paragraphs, sentences, words, etc.",
                                "required": ["mode"],
                            },
                            {
                                "title": "By Markdown header",
                                "type": "object",
                                "properties": {
                                    "mode": {
                                        "title": "Mode",
                                        "default": "markdown",
                                        "const": "markdown",
                                        "enum": ["markdown"],
                                        "type": "string",
                                    },
                                    "split_level": {
                                        "title": "Split level",
                                        "description": "Level of markdown headers to split text fields by. Headings down to the specified level will be used as split points",
                                        "default": 1,
                                        "minimum": 1,
                                        "maximum": 6,
                                        "type": "integer",
                                    },
                                },
                                "description": "Split the text by Markdown headers down to the specified header level. If the chunk size fits multiple sections, they will be combined into a single chunk.",
                                "required": ["mode"],
                            },
                            {
                                "title": "By Programming Language",
                                "type": "object",
                                "properties": {
                                    "mode": {
                                        "title": "Mode",
                                        "default": "code",
                                        "const": "code",
                                        "enum": ["code"],
                                        "type": "string",
                                    },
                                    "language": {
                                        "title": "Language",
                                        "description": "Split code in suitable places based on the programming language",
                                        "enum": [
                                            "cpp",
                                            "go",
                                            "java",
                                            "js",
                                            "php",
                                            "proto",
                                            "python",
                                            "rst",
                                            "ruby",
                                            "rust",
                                            "scala",
                                            "swift",
                                            "markdown",
                                            "latex",
                                            "html",
                                            "sol",
                                        ],
                                        "type": "string",
                                    },
                                },
                                "required": ["language", "mode"],
                                "description": "Split the text by suitable delimiters based on the programming language. This is useful for splitting code into chunks.",
                            },
                        ],
                    },
                    "field_name_mappings": {
                        "title": "Field name mappings",
                        "description": "List of fields to rename. Not applicable for nested fields, but can be used to rename fields already flattened via dot notation.",
                        "default": [],
                        "type": "array",
                        "items": {
                            "title": "FieldNameMappingConfigModel",
                            "type": "object",
                            "properties": {
                                "from_field": {
                                    "title": "From field name",
                                    "description": "The field name in the source",
                                    "type": "string",
                                },
                                "to_field": {
                                    "title": "To field name",
                                    "description": "The field name to use in the destination",
                                    "type": "string",
                                },
                            },
                            "required": ["from_field", "to_field"],
                        },
                    },
                },
                "required": ["chunk_size"],
                "group": "processing",
            },
        },
        "required": ["indexing", "embedding", "processing"],
        "groups": [
            {"id": "processing", "title": "Processing"},
            {"id": "embedding", "title": "Embedding"},
            {"id": "indexing", "title": "Indexing"},
        ],
    }
    assert ConfigModel.schema() == expected
