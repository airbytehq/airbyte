#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from abc import abstractmethod
from typing import Any, Dict, List, Optional

import dpath
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.utils import schema_helpers
from pydantic.v1 import AnyUrl, BaseModel, Field


class AbstractFileBasedSpec(BaseModel):
    """
    Used during spec; allows the developer to configure the cloud provider specific options
    that are needed when users configure a file-based source.
    """

    start_date: Optional[str] = Field(
        title="Start Date",
        description="UTC date and time in the format 2017-01-25T00:00:00.000000Z. Any file modified before this date will not be replicated.",
        examples=["2021-01-01T00:00:00.000000Z"],
        format="date-time",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}Z$",
        pattern_descriptor="YYYY-MM-DDTHH:mm:ss.SSSSSSZ",
        order=1,
    )

    streams: List[FileBasedStreamConfig] = Field(
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
        transformed_schema: Dict[str, Any] = copy.deepcopy(schema)
        schema_helpers.expand_refs(transformed_schema)
        cls.replace_enum_allOf_and_anyOf(transformed_schema)
        cls.remove_discriminator(transformed_schema)

        return transformed_schema

    @staticmethod
    def remove_discriminator(schema: Dict[str, Any]) -> None:
        """pydantic adds "discriminator" to the schema for oneOfs, which is not treated right by the platform as we inline all references"""
        dpath.delete(schema, "properties/**/discriminator")

    @staticmethod
    def replace_enum_allOf_and_anyOf(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        allOfs are not supported by the UI, but pydantic is automatically writing them for enums.
        Unpacks the enums under allOf and moves them up a level under the enum key
        anyOfs are also not supported by the UI, so we replace them with the similar oneOf, with the
        additional validation that an incoming config only matches exactly one of a field's types.
        """
        objects_to_check = schema["properties"]["streams"]["items"]["properties"]["format"]
        objects_to_check["type"] = "object"
        objects_to_check["oneOf"] = objects_to_check.pop("anyOf", [])
        for format in objects_to_check["oneOf"]:
            for key in format["properties"]:
                object_property = format["properties"][key]
                AbstractFileBasedSpec.move_enum_to_root(object_property)

        properties_to_change = ["validation_policy"]
        for property_to_change in properties_to_change:
            property_object = schema["properties"]["streams"]["items"]["properties"][property_to_change]
            if "anyOf" in property_object:
                schema["properties"]["streams"]["items"]["properties"][property_to_change]["type"] = "object"
                schema["properties"]["streams"]["items"]["properties"][property_to_change]["oneOf"] = property_object.pop("anyOf")
            AbstractFileBasedSpec.move_enum_to_root(property_object)

        csv_format_schemas = list(
            filter(
                lambda format: format["properties"]["filetype"]["default"] == "csv",
                schema["properties"]["streams"]["items"]["properties"]["format"]["oneOf"],
            )
        )
        if len(csv_format_schemas) != 1:
            raise ValueError(f"Expecting only one CSV format but got {csv_format_schemas}")
        csv_format_schemas[0]["properties"]["header_definition"]["oneOf"] = csv_format_schemas[0]["properties"]["header_definition"].pop(
            "anyOf", []
        )
        csv_format_schemas[0]["properties"]["header_definition"]["type"] = "object"
        return schema

    @staticmethod
    def move_enum_to_root(object_property: Dict[str, Any]) -> None:
        if "allOf" in object_property and "enum" in object_property["allOf"][0]:
            object_property["enum"] = object_property["allOf"][0]["enum"]
            object_property.pop("allOf")
