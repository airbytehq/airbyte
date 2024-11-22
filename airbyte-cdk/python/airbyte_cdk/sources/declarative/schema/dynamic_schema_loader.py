#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any, List, Mapping, Optional, Union

import dpath
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.types import Config


@dataclass(frozen=True)
class TypesPair:
    target_type: str
    current_type: Union[InterpolatedString, str]


@dataclass
class SchemaTypeIdentifier:
    schema_pointer: List[Union[InterpolatedString, str]]
    key_pointer: List[Union[InterpolatedString, str]]
    parameters: InitVar[Mapping[str, Any]]
    type_pointer: Optional[List[Union[InterpolatedString, str]]] = None
    types_map: List[TypesPair] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.schema_pointer = self._update_pointer(pointer=self.schema_pointer, parameters=parameters)
        self.key_pointer = self._update_pointer(pointer=self.key_pointer, parameters=parameters)
        self.type_pointer = self._update_pointer(pointer=self.type_pointer, parameters=parameters) if self.type_pointer else None

    @staticmethod
    def _update_pointer(
        pointer: Optional[List[Union[InterpolatedString, str]]], parameters
    ) -> Optional[List[Union[InterpolatedString, str]]]:
        _pointer = [InterpolatedString.create(path, parameters=parameters) for path in pointer]
        for path_index in range(len(pointer)):
            if isinstance(pointer[path_index], str):
                _pointer[path_index] = InterpolatedString.create(pointer[path_index], parameters=parameters)

        return _pointer


@dataclass
class DynamicSchemaLoader(SchemaLoader):
    retriever: Retriever
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    schema_type_identifier: SchemaTypeIdentifier
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def _replace_type_if_not_valid(self, field_type):
        for types_pair in self.schema_type_identifier.types_map:
            if field_type == types_pair.current_type:
                return types_pair.target_type
        return field_type

    def get_json_schema(self) -> Mapping[str, Any]:
        response_json = next(self.retriever.read_records({}), None)

        raw_schema = self._extract_data(response_json, self.schema_type_identifier.schema_pointer) if response_json else []

        # For each property definition in the raw schema:
        # - Extract `field_key` using `self.schema_type_identifier.key_pointer` and ensure it's a valid string.
        # - Extract `field_type` using `self.schema_type_identifier.type_pointer`, defaulting to "string" if not provided.
        # - Validate `field_type`:
        #   - It should be either a string (e.g., "string", "integer") or
        #   - A list of exactly two strings (e.g., ["string", "null"]). As normalization do not support more than two types.
        # - If all conditions are met, add the key-value pair to the `properties` dictionary.
        properties = {
            field_key: {"type": field_type}
            for property_definition in raw_schema
            if (field_key := self._extract_data(property_definition, self.schema_type_identifier.key_pointer))
            and isinstance(field_key, str)
            and (
                field_type := self._replace_type_if_not_valid(self._extract_data(property_definition, self.schema_type_identifier.type_pointer, default="string"))
                if self.schema_type_identifier.type_pointer
                else "string"
            )
            and (
                isinstance(field_type, str)
                or (isinstance(field_type, list) and len(field_type) == 2 and all(isinstance(item, str) for item in field_type))
            )
        }

        if len(properties) != len(raw_schema):
            raise ValueError("Invalid field key or type detected in raw schema.")

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }

    def _extract_data(self, body, extraction_path, default=None):
        """
        Extract data from the response body based on the configured field path.
        """

        if len(extraction_path) == 0:
            return body

        path = [path.eval(self.config) for path in extraction_path]

        if "*" in path:
            extracted = dpath.values(body, path)
        else:
            extracted = dpath.get(body, path, default=default)

        return extracted
