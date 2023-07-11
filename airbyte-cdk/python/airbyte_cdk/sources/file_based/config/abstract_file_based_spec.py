#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import re
from abc import abstractmethod
from typing import Any, Dict, List

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from jsonschema import RefResolver
from pydantic import AnyUrl, BaseModel, Field


class AbstractFileBasedSpec(BaseModel):
    """
    Used during spec; allows the developer to configure the cloud provider specific options
    that are needed when users configure a file-based source.
    """

    streams: List[FileBasedStreamConfig] = Field(
        title="The list of streams to sync",
        description="Streams defines the behavior for grouping files together that will be synced to the downstream destination. Each "
        "stream has it own independent configuration to handle which files to sync, how files should be parsed, and the "
        "validation of records against the schema.",
        order=10,
    )

    @classmethod
    @abstractmethod
    def documentation_url(cls) -> AnyUrl:
        """
        :return: link to docs page for this source e.g. "https://docs.airbyte.com/integrations/sources/s3"
        """

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generates the mapping comprised of the config fields
        """
        schema = super().schema(*args, **kwargs)
        resolved_schema = cls.resolve_refs(schema)
        resolved_schema = cls.add_legacy_format(resolved_schema)

        return resolved_schema

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

    @staticmethod
    def add_legacy_format(schema: dict) -> dict:
        """
        Because we still need to allow for configs using the legacy format (like source-s3) where file format options
        are at the top level and not mapped from file_type -> format options, the json schema used to validate the
        config must be adjusted to support the generic mapping object. Once configs no longer adhere to the old
        format we can remove this change.
        """
        csv_format_options = schema["properties"]["streams"]["items"]["properties"]["format"]
        union_format = {"anyOf": [csv_format_options, {"type": "object"}]}
        schema["properties"]["streams"]["items"]["properties"]["format"] = union_format
        return schema
