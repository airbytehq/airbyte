#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Union

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.utils import schema_helpers
from pydantic import AnyUrl, BaseModel, Field

from airbyte_cdk.sources.file_based.config.avro_format import AvroFormat
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from airbyte_cdk.sources.file_based.config.jsonl_format import JsonlFormat
from airbyte_cdk.sources.file_based.config.parquet_format import ParquetFormat


class AbstractFileBasedSpec(BaseModel):
    """
    Used during spec; allows the developer to configure the cloud provider specific options
    that are needed when users configure a file-based source.
    """

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
        # schema = super().schema(*args, **kwargs)
        # transformed_schema = copy.deepcopy(schema)
        # schema_helpers.expand_refs(transformed_schema)
        # cls.replace_enum_allOf_and_anyOf(transformed_schema)
        transformed_schema = {
            'title': 'Config',
            'description': 'Used during spec; allows the developer to configure the cloud provider specific options\nthat are needed when users configure a file-based source.',
            'type': 'object',
            'properties': {
                'streams': {
                    'title': 'The list of streams to sync',
                    'description': 'Each instance of this configuration defines a <a href="https://docs.airbyte.com/cloud/core-concepts#stream">stream</a>. Use this to define which files belong in the stream, their format, and how they should be parsed and validated. When sending data to warehouse destination such as Snowflake or BigQuery, each stream is a separate table.',
                    'order': 10,
                    'type': 'array',
                    'items': {
                        'title': 'FileBasedStreamConfig',
                        'type': 'object',
                        'properties': {
                            'name': {
                                'title': 'Name',
                                'description': 'The name of the stream.',
                                'type': 'string'
                            },
                            'format': {
                                'title': 'Format',
                                'type': 'object',
                                'oneOf': [
                                    {
                                        'title': 'Avro Format',
                                        'type': 'object',
                                        'properties': {
                                            'filetype': {
                                                'title': 'Filetype',
                                                'const': 'avro',
                                                'type': 'string'
                                            },
                                            'decimal_as_float': {
                                                'title': 'Convert Decimal Fields to Floats',
                                                'description': 'Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.',
                                                'default': False,
                                                'type': 'boolean'
                                            }
                                        }
                                    }, {
                                        'title': 'CSV Format',
                                        'type': 'object',
                                        'properties': {
                                            'filetype': {
                                                'title': 'Filetype',
                                                'const': 'csv',
                                                'type': 'string'
                                            },
                                            'delimiter': {
                                                'title': 'Delimiter',
                                                'description': "The character delimiting individual cells in the CSV data. This may only be a 1-character string. For tab-delimited data enter '\\t'.",
                                                'default': ',',
                                                'type': 'string'
                                            }
                                        }
                                    }
                                ]
                            },
                            'globs': {
                                'title': 'Globs',
                                'description': 'The pattern used to specify which files should be selected from the file system. For more information on glob pattern matching look <a href="https://en.wikipedia.org/wiki/Glob_(programming)">here</a>.',
                                'type': 'array',
                                'items': {'type': 'string'}
                            },
                            'validation_policy': {
                                'title': 'Validation Policy',
                                'description': 'The name of the validation policy that dictates sync behavior when a record does not adhere to the stream schema.',
                                'enum': ['Emit Record', 'Skip Record','Wait for Discover']
                            }
                        },
                        'required': ['name', 'format', 'validation_policy']
                    }
                },
                'bucket': {
                    'title': 'Bucket',
                    'description': 'Name of the S3 bucket where the file(s) exist.',
                    'order': 0,
                    'type': 'string'
                },
            },
            'required': ['streams', 'bucket']
        }

        return transformed_schema

    @staticmethod
    def replace_enum_allOf_and_anyOf(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        allOfs are not supported by the UI, but pydantic is automatically writing them for enums.
        Unpacks the enums under allOf and moves them up a level under the enum key
        anyOfs are also not supported by the UI, so we replace them with the similar oneOf, with the
        additional validation that an incoming config only matches exactly one of a field's types.
        """
        objects_to_check = schema["properties"]["streams"]["items"]["properties"]["file_type"]
        objects_to_check["type"] = "object"
        [all_of] = objects_to_check.pop("allOf")
        objects_to_check["properties"] = all_of["properties"]
        objects_to_check["properties"]["format"]["oneOf"] = objects_to_check["properties"]["format"].pop("anyOf")

        # for format in objects_to_check["oneOf"]:
        #     for key in format["properties"]:
        #         object_property = format["properties"][key]
        #         if "allOf" in object_property and "enum" in object_property["allOf"][0]:
        #             object_property["enum"] = object_property["allOf"][0]["enum"]
        #             object_property.pop("allOf")

        properties_to_change = ["validation_policy"]
        for property_to_change in properties_to_change:
            property_object = schema["properties"]["streams"]["items"]["properties"][property_to_change]
            if "anyOf" in property_object:
                schema["properties"]["streams"]["items"]["properties"][property_to_change]["type"] = "object"
                schema["properties"]["streams"]["items"]["properties"][property_to_change]["oneOf"] = property_object.pop("anyOf")
            if "allOf" in property_object and "enum" in property_object["allOf"][0]:
                property_object["enum"] = property_object["allOf"][0]["enum"]
                property_object.pop("allOf")

        # properties_to_change = ["file_type"]
        # for property_to_change in properties_to_change:
        #     property_object = schema["properties"]["streams"]["items"]["properties"][property_to_change]
        #     if "anyOf" in property_object:
        #         schema["properties"]["streams"]["items"]["properties"][property_to_change]["type"] = "object"
        #         schema["properties"]["streams"]["items"]["properties"][property_to_change]["oneOf"] = property_object.pop("anyOf")
        #     if "allOf" in property_object and "enum" in property_object["allOf"][0]:
        #         property_object["oneOf"] = property_object.pop("allOf")
        #
        #
        # properties_to_change = ["format"]
        # for property_to_change in properties_to_change:
        #     for k, item in schema["properties"]["streams"]["items"]["properties"]["file_type"].items():
        #         if "anyOf" in item:
        #             schema["properties"]["streams"]["items"]["properties"][property_to_change]["type"] = "object"
        #             schema["properties"]["streams"]["items"]["properties"][property_to_change]["oneOf"] = item.pop("anyOf")
        #         if "allOf" in item:
        #             item["enum"] = item.pop("allOf")

        return schema
