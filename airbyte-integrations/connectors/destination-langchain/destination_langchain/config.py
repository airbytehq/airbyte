#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import re
from typing import List, Literal, Optional, Union

import dpath.util
from airbyte_cdk.destinations.vector_db_based.embedder import FakeEmbeddingConfigModel, OpenAIEmbeddingConfigModel
from jsonschema import RefResolver
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
        ...,
        title="Text fields to embed",
        description="List of fields in the record that should be used to calculate the embedding. All other fields are passed along as meta fields. The field list is applied to all streams in the same way and non-existing fields are ignored. If none are defined, all fields are considered text fields. When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.",
        always_show=True,
        examples=["text", "user.name", "users.*.name"],
    )

    class Config:
        schema_extra = {"group": "processing"}


class PineconeIndexingModel(BaseModel):
    mode: Literal["pinecone"] = Field("pinecone", const=True)
    pinecone_key: str = Field(..., title="Pinecone API key", airbyte_secret=True)
    pinecone_environment: str = Field(..., title="Pinecone environment", description="Pinecone environment to use")
    index: str = Field(..., title="Index", description="Pinecone index to use")

    class Config:
        title = "Pinecone"
        schema_extra = {
            "description": "Pinecone is a popular vector store that can be used to store and retrieve embeddings. It is a managed service and can also be queried from outside of langchain."
        }


class ChromaLocalIndexingModel(BaseModel):
    mode: Literal["chroma_local"] = Field("chroma_local", const=True)
    destination_path: str = Field(
        ...,
        title="Destination Path",
        description="Path to the directory where chroma files will be written. The files will be placed inside that local mount.",
        examples=["/local/my_chroma_db"],
    )
    collection_name: str = Field(
        title="Collection Name",
        description="Name of the collection to use.",
        default="langchain",
    )

    class Config:
        title = "Chroma (local persistance)"
        schema_extra = {
            "description": "Chroma is a popular vector store that can be used to store and retrieve embeddings. It will build its index in memory and persist it to disk by the end of the sync."
        }


class DocArrayHnswSearchIndexingModel(BaseModel):
    mode: Literal["DocArrayHnswSearch"] = Field("DocArrayHnswSearch", const=True)
    destination_path: str = Field(
        ...,
        title="Destination Path",
        description="Path to the directory where hnswlib and meta data files will be written. The files will be placed inside that local mount. All files in the specified destination directory will be deleted on each run.",
        examples=["/local/my_hnswlib_index"],
    )

    class Config:
        title = "DocArrayHnswSearch"
        schema_extra = {
            "description": "DocArrayHnswSearch is a lightweight Document Index implementation provided by Docarray that runs fully locally and is best suited for small- to medium-sized datasets. It stores vectors on disk in hnswlib, and stores all other data in SQLite."
        }


class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[OpenAIEmbeddingConfigModel, FakeEmbeddingConfigModel] = Field(
        ..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object"
    )
    indexing: Union[PineconeIndexingModel, DocArrayHnswSearchIndexingModel, ChromaLocalIndexingModel] = Field(
        ..., title="Indexing", description="Indexing configuration", discriminator="mode", group="indexing", type="object"
    )

    class Config:
        title = "Langchain Destination Config"
        schema_extra = {
            "groups": [
                {"id": "processing", "title": "Processing"},
                {"id": "embedding", "title": "Embedding"},
                {"id": "indexing", "title": "Indexing"},
            ]
        }

    @staticmethod
    def resolve_refs(schema: dict) -> dict:
        # config schemas can't contain references, so inline them
        json_schema_ref_resolver = RefResolver.from_schema(schema)
        str_schema = json.dumps(schema)
        for ref_block in re.findall(r'{"\$ref": "#\/definitions\/.+?(?="})"}', str_schema):
            ref = json.loads(ref_block)["$ref"]
            str_schema = str_schema.replace(ref_block, json.dumps(json_schema_ref_resolver.resolve(ref)[1]))
        pyschema: dict = json.loads(str_schema)
        del pyschema["definitions"]
        return pyschema

    @staticmethod
    def remove_discriminator(schema: dict) -> None:
        """pydantic adds "discriminator" to the schema for oneOfs, which is not treated right by the platform as we inline all references"""
        dpath.util.delete(schema, "properties/*/discriminator")

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = cls.resolve_refs(schema)
        cls.remove_discriminator(schema)
        return schema
