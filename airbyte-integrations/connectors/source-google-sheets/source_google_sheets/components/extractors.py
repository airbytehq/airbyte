#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping

import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor


@dataclass
class FieldMatchingExtractor(DpathExtractor):
    """ "
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
        self._properties_to_match = FieldMatchingExtractor.extract_properties_to_match(parameters["properties_to_match"], property_to_match_key)

    @staticmethod
    def extract_properties_to_match(properties_to_match, property_to_match_key):
        indexed_properties = {
            index: item_for_match[property_to_match_key] for index, item_for_match in enumerate(properties_to_match)
        }
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
