#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from abc import abstractmethod
from typing import Any, Dict, List

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.utils import schema_helpers
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
        transformed_schema = copy.deepcopy(schema)
        schema_helpers.expand_refs(transformed_schema)
        cls.remove_enum_allOf(transformed_schema)
        cls.add_legacy_format(transformed_schema)

        return transformed_schema

    @staticmethod
    def remove_enum_allOf(schema: dict) -> dict:
        """
        allOfs are not supported by the UI, but pydantic is automatically writing them for enums.
        Unpacks the enums under allOf and moves them up a level under the enum key
        """
        # this will need to add ["anyOf"] once we have more than one format type and loop over the list of elements
        objects_to_check = schema["properties"]["streams"]["items"]["properties"]["format"]
        if "additionalProperties" in objects_to_check:
            for key in objects_to_check["additionalProperties"]["properties"]:
                object_property = objects_to_check["additionalProperties"]["properties"][key]
                if "allOf" in object_property and "enum" in object_property["allOf"][0]:
                    object_property["enum"] = object_property["allOf"][0]["enum"]
                    object_property.pop("allOf")
        return schema

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
