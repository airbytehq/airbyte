from ast import Dict
from typing import Any, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from jsonschema import RefResolver
import json
import re


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
        description="List of fields in the record that should be used to calculate the embedding. All other fields are passed along as meta fields. If none are defined, all fields are considered text fields",
        always_show=True
    )

    class Config:
        schema_extra = {"group":"processing"}


class OpenAIEmbeddingConfigModel(BaseModel):
    mode: Literal["openai"] = Field("openai", const=True)
    openai_key: str = Field(..., title="OpenAI API key", airbyte_secret=True)

    class Config:
        title="OpenAI"

class FakeEmbeddingConfigModel(BaseModel):
    mode: Literal["fake"] = Field("fake", const=True)

    class Config:
        title="Fake"


class PineconeIndexingModel(BaseModel):
    mode: Literal["pinecone"] = Field("pinecone", const=True)
    pinecone_key: str = Field(..., title="Pinecone API key", airbyte_secret=True)
    pinecone_environment: str = Field(..., title="Pinecone environment", description="Pinecone environment to use")
    index: str = Field(..., title="Index", description="Pinecone index to use")

    class Config:
        title="Pinecone"


class DocArrayHnswSearchIndexingModel(BaseModel):
    mode: Literal["DocArrayHnswSearch"] = Field("DocArrayHnswSearch", const=True)
    destination_path: str = Field(
        ...,
        title="Destination Path",
        description="Path to the directory where hnswlib and meta data files will be written. The files will be placed inside that local mount.",
        examples=["/json_data"],
    )

    class Config:
        title="DocArrayHnswSearch"
        schema_extra={"description": "DocArrayHnswSearch is a lightweight Document Index implementation provided by Docarray that runs fully locally and is best suited for small- to medium-sized datasets. It stores vectors on disk in hnswlib, and stores all other data in SQLite."}

class ConfigModel(BaseModel):
    processing: ProcessingConfigModel
    embedding: Union[OpenAIEmbeddingConfigModel, FakeEmbeddingConfigModel] = Field(
        ..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object"
    )
    indexing: Union[PineconeIndexingModel, DocArrayHnswSearchIndexingModel] = Field(
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

    @classmethod
    def schema(cls):
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema()
        schema = cls.resolve_refs(schema)
        return schema