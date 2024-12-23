#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.types import Config
from source_google_sheets.utils import safe_name_conversion


@dataclass
class FieldMatchingExtractor(DpathExtractor):
    """
    Current DpathExtractor has problems for this type of data in response:
    [
      {
        "values": [
          [
            "name1",
            "22"
          ],
          [
            "name2",
            "24"
          ],
          [
            "name3",
            "25"
          ]
        ]
      }
    ]

    This is because "values" field is a list of lists instead of objects that we could extract with "*".
    In order to do so we need the ordered properties from the schema that we can match with each list of values.
    Then, if we get a properties object like {0: 'name', 1: 'age'} we end up with:

    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name1","age":"22"},"emitted_at":1734371904128}}
    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name2","age":"24"},"emitted_at":1734371904134}}
    {"type":"RECORD","record":{"stream":"a_stream_name","data":{"name":"name3","age":"25"},"emitted_at":1734371904134}}
    """

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._values_to_match_key = parameters["values_to_match_key"]
        property_to_match_key = parameters["property_to_match_key"]
        self._properties_to_match = FieldMatchingExtractor.extract_properties_to_match(
            parameters["properties_to_match"], property_to_match_key
        )

    @staticmethod
    def extract_properties_to_match(properties_to_match, property_to_match_key):
        indexed_properties = {index: item_for_match[property_to_match_key] for index, item_for_match in enumerate(properties_to_match)}
        return indexed_properties

    @staticmethod
    def match_properties_with_values(unmatched_values: List[str], ordered_properties: Dict[int, str]):
        data = {}
        for relevant_index in sorted(ordered_properties.keys()):
            if relevant_index >= len(unmatched_values):
                break

            unmatch_value = unmatched_values[relevant_index]
            if unmatch_value.strip() != "":
                data[ordered_properties[relevant_index]] = unmatch_value
        yield data

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        raw_records_extracted = super().extract_records(response=response)
        for raw_record in raw_records_extracted:
            unmatched_values_collection = raw_record[self._values_to_match_key]
            for unmatched_values in unmatched_values_collection:
                yield from FieldMatchingExtractor.match_properties_with_values(unmatched_values, self._properties_to_match)


class NamesConversionForRawSchema:
    config: Config

    def _extract_data(
        self,
        body: Mapping[str, Any],
        extraction_path: Optional[List[Union[InterpolatedString, str]]] = None,
        default: Any = None,
    ) -> Any:
        """
        Extracts data from the body based on the provided extraction path.
        """

        if not extraction_path:
            return body

        path = [node.eval(self.config) if not isinstance(node, str) else node for node in extraction_path]

        return dpath.get(body, path, default=default)  # type: ignore # extracted

    def _set_data(
        self, value: Any, body: MutableMapping[str, Any], extraction_path: Optional[List[Union[InterpolatedString, str]]] = None
    ) -> Any:
        """
        Sets data in the body based on the provided extraction path.
        """
        if not extraction_path:
            body = value

        path = [node.eval(self.config) if not isinstance(node, str) else node for node in extraction_path]

        dpath.set(body, path, value=value)

    def convert(self, schema_type_identifier, records: Iterable[MutableMapping[Any, Any]]):
        schema_pointer = schema_type_identifier.get("schema_pointer")
        key_pointer = schema_type_identifier["key_pointer"]
        for record in records:
            raw_schema_properties = self._extract_data(record, schema_pointer)

            for raw_schema_property in raw_schema_properties:
                raw_schema_property_value = self._extract_data(raw_schema_property, key_pointer)
                converted_value = self._convert_value(raw_schema_property_value)
                self._set_data(converted_value, raw_schema_property, key_pointer)
            yield record

    @staticmethod
    def _convert_value(value: str):
        return safe_name_conversion(value)


class DpathSchemaExtractor(DpathExtractor, NamesConversionForRawSchema):
    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self.names_conversion = self.config.get("names_conversion", False)
        self.schema_type_identifier = parameters["schema_type_identifier"]

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        extracted_records = super().extract_records(response=response)
        if self.names_conversion:
            yield from self.convert(schema_type_identifier=self.schema_type_identifier, records=extracted_records)
        yield from extracted_records
