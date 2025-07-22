#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.auth.token import ApiKeyAuthenticator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.auth.token_provider import TokenProvider
from airbyte_cdk.sources.types import Config

@dataclass
class EventsRecordExtractor(DpathExtractor):
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        jsonl_records = super().extract_records(response=response)
        for record_dict in jsonl_records:
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)
            yield {**record_dict_common_fields, "data": record_dict}

@dataclass
class IterableTokenProvider(TokenProvider):
    config: Config

    def get_token(self) -> str:
        return self.config["api_key"]

@dataclass
class UsersSchemaLoader(SchemaLoader):
    config: Config
    name: str = "users"

    objects: Mapping[str, Any] = field(default_factory=dict)
    schema: Mapping[str, Any] = field(default_factory=dict)

    def _get_field_schema(self, field_type: str) -> Mapping[str, Any]:
        match field_type:
            case "string":
                return {
                    "type": [
                        "null",
                        "string"
                    ]
                }
            case "date":
                return {
                    "type": [
                        "null",
                        "string"
                    ],
                    "format": "date-time"
                }
            case "long":
                return {
                    "type": [
                        "null",
                        "number"
                    ]
                }
            case "double":
                return {
                    "type": [
                        "null",
                        "number"
                    ]}
            case "boolean":
                return {
                    "type": [
                        "null",
                        "boolean"
                    ]
                }
            case "geo_location":
                return {
                    "type": [
                        "null",
                        "object"
                    ],
                    "properties": {
                        "lat": {
                            "type": [
                                "null",
                                "number"
                            ]
                        },
                        "lon": {
                            "type": [
                                "null",
                                "number"
                            ]
                        }
                    }
                }
            case "nested":
                return {
                    "type": [
                        "null",
                        "object"
                    ],
                    "properties": {}
                }
            case "object":
                return {
                    "type": [
                        "null",
                        "object"
                    ],
                    "properties": {}
                }
            case _:
                return {
                    "type": [
                        "null",
                        "string"
                    ]
                }

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.schema:
            return self.schema

        schema = {
            "properties": {},
            "type": ["null", "object"]
        }

        # Setup the requester to be able to get the fields from the Iterable API
        request_option = RequestOption(field_name="Api-Key", inject_into=RequestOptionType.header, parameters={})
        token_provider = IterableTokenProvider(config=self.config)
        authenticator = ApiKeyAuthenticator(config=self.config, request_option=request_option, token_provider=token_provider, parameters={})

        # Get the fields from the Iterable API
        requester = HttpRequester(
            name="users_get_fields",
            config=self.config,
            parameters={"name": self.name},
            url_base="https://api.iterable.com/api/",
            path="users/getFields",
            http_method="GET",
            authenticator=authenticator,
        )

        response = requester.send_request()

        if not response.ok:
            raise Exception(f"Failed to get fields from Iterable API: {response.text}")

        fields = response.json().get("fields", {})

        if not fields:
            raise Exception("No fields found in Iterable API")

        # Sort and iterate through the fields to build the schema
        for field_name, field_type in sorted(fields.items()):
            # Split up field names with periods to determine if this is a nested field/object
            path_parts = field_name.split('.')

            if len(path_parts) > 1:
                # We are dealing with a nested field or object
                parent_path = path_parts[:-1]
                child_field_name = path_parts[-1]

                # Start at the top-level objects and traverse down to the direct parent of the field/object
                current_level_obj = self.objects
                parent_obj = None
                for part in parent_path:
                    if isinstance(current_level_obj, dict) and part in current_level_obj:
                        parent_obj = current_level_obj[part]
                        current_level_obj = parent_obj.get("properties", {})

                        continue

                    raise Exception(f"Parent object at path '{'.'.join(parent_path)}' not found for field '{field_name}'.")

                # Add the field/object to the parent object
                parent_obj["properties"][child_field_name] = self._get_field_schema(field_type)

                continue

            # We are dealing with a top-level field or object
            if field_type == "object" or field_type == "nested":
                # Add the base object schema
                self.objects[field_name] = self._get_field_schema(field_type)
            else:
                schema["properties"][field_name] = self._get_field_schema(field_type)

        # Last step is to add the processed objects to the schema
        for object_name, object_schema in self.objects.items():
            schema["properties"][object_name] = object_schema

        # Cache the schema in the class
        self.schema = schema

        return schema
