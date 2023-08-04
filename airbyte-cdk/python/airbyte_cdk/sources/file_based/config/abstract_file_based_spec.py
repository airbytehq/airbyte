#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from abc import abstractmethod
from typing import Any, Dict, List, Generic, TypeVar

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig, ValidFormatType
from airbyte_cdk.sources.utils import schema_helpers
from pydantic import AnyUrl, BaseModel, Field


FileBasedStreamConfigType = TypeVar("FileBasedStreamConfigType", bound="FileBasedStreamConfig")

class AbstractFileBasedSpec(BaseModel, Generic[FileBasedStreamConfigType]):
    """
    Used during spec; allows the developer to configure the cloud provider specific options
    that are needed when users configure a file-based source.
    """

    streams: List[FileBasedStreamConfigType] = Field(
        title="The list of streams to sync",
        description='Each instance of this configuration defines a <a href="https://docs.airbyte.com/cloud/core-concepts#stream">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table.',
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
        config_schema = cls.__orig_bases__[0].__args__[0].schema()
        transformed_schema = copy.deepcopy(schema)
        schema_helpers.expand_refs(transformed_schema)

        # This is a little wild
        # We replace the format field with the format field from the config schema, which is a specialized template
        transformed_schema["properties"]["streams"]["items"]["properties"]["format"] = config_schema["properties"]["format"]

        cls.replace_enum_allOf_and_anyOf(transformed_schema)

        return transformed_schema
    @staticmethod
    def replace_enum_allOf_and_anyOf(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        allOfs are not supported by the UI, but pydantic is automatically writing them for enums.
        Unpacks the enums under allOf and moves them up a level under the enum key
        anyOfs are also not supported by the UI, so we replace them with the similar oneOf, with the
        additional validation that an incoming config only matches exactly one of a field's types.
        """
        objects_to_check = schema["properties"]["streams"]["items"]["properties"]["format"]
        objects_to_check["oneOf"] = objects_to_check.pop("anyOf", [])
        for format in objects_to_check["oneOf"]:
            for key in format["properties"]:
                object_property = format["properties"][key]
                if "allOf" in object_property and "enum" in object_property["allOf"][0]:
                    object_property["enum"] = object_property["allOf"][0]["enum"]
                    object_property.pop("allOf")

        properties_to_change = ["primary_key", "validation_policy"]
        for property_to_change in properties_to_change:
            property_object = schema["properties"]["streams"]["items"]["properties"][property_to_change]
            if "anyOf" in property_object:
                schema["properties"]["streams"]["items"]["properties"][property_to_change]["oneOf"] = property_object.pop("anyOf")
            if "allOf" in property_object and "enum" in property_object["allOf"][0]:
                property_object["enum"] = property_object["allOf"][0]["enum"]
                property_object.pop("allOf")
        return schema
