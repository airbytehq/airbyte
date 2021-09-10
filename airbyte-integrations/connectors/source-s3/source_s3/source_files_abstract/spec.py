#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import re
from copy import deepcopy
from typing import Union

from jsonschema import RefResolver
from pydantic import BaseModel, Field

from .formats.csv_spec import CsvFormat
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
        description="This source creates one table per connection, this field is the name of that table. This should include only letters, numbers, dash and underscores. Note that this may be altered according to destination.",
    )

    path_pattern: str = Field(
        description='Add at least 1 pattern here to match filepaths against. Use | to separate multiple patterns. Airbyte uses these patterns to determine which files to pick up from the provider storage. See <a href="https://facelessuser.github.io/wcmatch/glob/" target="_blank">wcmatch.glob</a> to understand pattern syntax (GLOBSTAR and SPLIT flags are enabled). Use pattern <strong>**</strong> to pick up all files.',
        examples=["**", "myFolder/myTableFiles/*.csv|myFolder/myOtherTableFiles/*.csv"],
    )

    user_schema: str = Field(
        alias="schema",
        default="{}",
        description='Optionally provide a schema to enforce, as a valid JSON string. Ensure this is a mapping of <strong>{ "column" : "type" }</strong>, where types are valid <a href="https://json-schema.org/understanding-json-schema/reference/type.html" target="_blank">JSON Schema datatypes</a>. Leave as {} to auto-infer the schema.',
        examples=['{"column_1": "number", "column_2": "string", "column_3": "array", "column_4": "object", "column_5": "boolean"}'],
    )

    format: Union[CsvFormat, ParquetFormat] = Field(default=CsvFormat.Config.title)

    @staticmethod
    def change_format_to_oneOf(schema: dict) -> dict:
        schema["properties"]["format"]["type"] = "object"
        if "oneOf" in schema["properties"]["format"]:
            return schema
        schema["properties"]["format"]["oneOf"] = deepcopy(schema["properties"]["format"]["anyOf"])
        del schema["properties"]["format"]["anyOf"]
        return schema

    @staticmethod
    def check_provider_added(schema: dict) -> dict:
        if "provider" not in schema["properties"]:
            raise RuntimeError("You must add the 'provider' property in your child spec class")

    @staticmethod
    def resolve_refs(schema: dict) -> dict:
        json_schema_ref_resolver = RefResolver.from_schema(schema)
        str_schema = json.dumps(schema)
        for ref_block in re.findall(r'{"\$ref": "#\/definitions\/.+?(?="})"}', str_schema):
            ref = json.loads(ref_block)["$ref"]
            str_schema = str_schema.replace(ref_block, json.dumps(json_schema_ref_resolver.resolve(ref)[1]))
        pyschema = json.loads(str_schema)
        del pyschema["definitions"]
        return pyschema

    @classmethod
    def schema(cls) -> dict:
        """ we're overriding the schema classmethod to enable some post-processing """
        schema = super().schema()
        cls.check_provider_added(schema)
        schema = cls.change_format_to_oneOf(schema)
        schema = cls.resolve_refs(schema)
        return schema
