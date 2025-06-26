#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import re
from typing import Any, Dict, Union

from jsonschema import RefResolver
from pydantic.v1 import BaseModel, Field

from .formats.avro_spec import AvroFormat
from .formats.csv_spec import CsvFormat
from .formats.jsonl_spec import JsonlFormat
from .formats.parquet_spec import ParquetFormat


# To implement your provider specific spec, inherit from SourceFilesAbstractSpec and add provider-specific settings e.g.:

# class SourceS3Spec(SourceFilesAbstractSpec, BaseModel):
#     class Config:
#         title="S3 Source Spec"

#     class S3Provider(BaseModel):
#         class Config:
#             title = "S3: Amazon Web Services"

#         bucket: str = Field(description="Name of the S3 bucket where the file(s) exist.")
#         aws_access_key_id: Optional[str] = Field(
#             default=None,
#             description="...",
#             airbyte_secret=True
#         )
#         aws_secret_access_key: Optional[str] = Field(
#             default=None,
#             description="...",
#             airbyte_secret=True
#         )
#         path_prefix: str = Field(
#             default="",
#             description="..."
#         )
#     provider: S3Provider = Field(...)  # leave this as Field(...), just change type to relevant class


class SourceFilesAbstractSpec(BaseModel):
    dataset: str = Field(
        pattern=r"^([A-Za-z0-9-_]+)$",
        description="The name of the stream you would like this source to output. Can contain letters, numbers, or underscores.",
        order=0,
        title="Output Stream Name",
    )

    path_pattern: str = Field(
        title="Pattern of files to replicate",
        description="A regular expression which tells the connector which files to replicate. All files which match this pattern will be "
        'replicated. Use | to separate multiple patterns. See <a href="https://facelessuser.github.io/wcmatch/glob/" target="_'
        'blank">this page</a> to understand pattern syntax (GLOBSTAR and SPLIT flags are enabled). '
        "Use pattern <strong>**</strong> to pick up all files.",
        examples=["**", "myFolder/myTableFiles/*.csv|myFolder/myOtherTableFiles/*.csv"],
        order=10,
    )

    format: Union[CsvFormat, ParquetFormat, AvroFormat, JsonlFormat] = Field(
        default="csv", title="File Format", description="The format of the files you'd like to replicate", order=20
    )

    user_schema: str = Field(
        title="Manually enforced data schema",
        alias="schema",
        default="{}",
        description="Optionally provide a schema to enforce, as a valid JSON string. Ensure this is a mapping of "
        '<strong>{ "column" : "type" }</strong>, where types are valid '
        '<a href="https://json-schema.org/understanding-json-schema/reference/type.html" target="_blank">JSON Schema '
        "datatypes</a>. Leave as {} to auto-infer the schema.",
        examples=['{"column_1": "number", "column_2": "string", "column_3": "array", "column_4": "object", "column_5": "boolean"}'],
        order=30,
    )

    @staticmethod
    def change_format_to_oneOf(schema: dict) -> dict:
        props_to_change = ["format"]
        for prop in props_to_change:
            schema["properties"][prop]["type"] = "object"
            if "oneOf" in schema["properties"][prop]:
                continue
            schema["properties"][prop]["oneOf"] = schema["properties"][prop].pop("anyOf")
        return schema

    @staticmethod
    def remove_enum_allOf(schema: dict) -> dict:
        """
        allOfs are not supported by the UI, but pydantic is automatically writing them for enums.
        Unpack them into the root
        """
        objects_to_check = schema["properties"]["format"]["oneOf"]
        for object in objects_to_check:
            for key in object["properties"]:
                property = object["properties"][key]
                if "allOf" in property and "enum" in property["allOf"][0]:
                    property["enum"] = property["allOf"][0]["enum"]
                    property.pop("allOf")
        return schema

    @staticmethod
    def check_provider_added(schema: dict) -> None:
        if "provider" not in schema["properties"]:
            raise RuntimeError("You must add the 'provider' property in your child spec class")

    @staticmethod
    def resolve_refs(schema: dict) -> dict:
        json_schema_ref_resolver = RefResolver.from_schema(schema)
        str_schema = json.dumps(schema)
        for ref_block in re.findall(r'{"\$ref": "#\/definitions\/.+?(?="})"}', str_schema):
            ref = json.loads(ref_block)["$ref"]
            str_schema = str_schema.replace(ref_block, json.dumps(json_schema_ref_resolver.resolve(ref)[1]))
        pyschema: dict = json.loads(str_schema)
        del pyschema["definitions"]
        return pyschema

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """we're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(*args, **kwargs)
        cls.check_provider_added(schema)
        schema = cls.change_format_to_oneOf(schema)
        schema = cls.resolve_refs(schema)
        schema = cls.remove_enum_allOf(schema)
        return schema
