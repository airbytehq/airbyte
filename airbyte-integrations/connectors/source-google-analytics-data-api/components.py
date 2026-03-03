#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from itertools import islice
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class CombinedExtractor(RecordExtractor):
    """
    Extractor that merges the output of multiple sub-extractors into a single record.
    This extractor takes a list of `RecordExtractor` instances (`extractors`), each of which
    independently extracts records from the response. For each response, the extractor:
    1. Invokes each sub-extractor to generate iterables of records.
    2. Zips the results together, so that the first record from each extractor is combined,
       the second from each, and so on.
    3. Merges each group of records into a single dictionary using `dict.update()`.
    The result is a sequence of dictionaries where each dictionary contains the merged keys
    and values from the corresponding records across all extractors.
    Example:
        keys_extractor -> yields: [{"name": "Alice", "age": 30}]
        extra_data_extractor -> yields: [{"country": "US"}]
        CombinedExtractor(extractors=[keys_extractor, extra_data_extractor]) ->
            yields: [{"name": "Alice", "age": 30, "country": "US"}]
    """

    extractors: List[RecordExtractor]

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        extractors_records = [extractor.extract_records(response) for extractor in self.extractors]

        for records in zip(*extractors_records):
            merged = {}
            for record in records:
                merged.update(record)  # merge all fields
            yield merged


@dataclass
class KeyValueExtractor(RecordExtractor):
    """
    Extractor that combines keys and values from two separate extractors.

    The `keys_extractor` and `values_extractor` extract records independently
    from the response. Their outputs are zipped together to form key-value mappings.

    Each key from `keys_extractor` should correspond to a key in the resulting dictionary,
    and each value from `values_extractor` is the value for that key.

    Example:
        keys_extractor -> yields: ["name", "age"]
        values_extractor -> yields: ["Alice", 30, "Brian", 32]
        result: { "name": "Alice", "age": 30 } and { "name": "Brian", "age": 32 }

    ---
    More specifically, we:
      - Start with a list of keys, e.g. ['date', 'firstUserCampaignName', 'firstUserMedium'].
      - Receive a flat sequence of values in that same order, e.g.:
        ['20231001', 'TikTok-Conversion', 'ads', '20231001', 'TikTok-Mahta', 'ads'].
      - Because there are three keys, we split the flat list into chunks of three values each.
        Each chunk maps to the keys to form one dictionary:
          {
              "date": "20231001",
              "firstUserCampaignName": "TikTok-Conversion",
              "firstUserMedium": "ads"
          }
        and so on.

    This allows transforming a flat list of values into structured records using a predefined key schema.
    """

    keys_extractor: RecordExtractor
    values_extractor: RecordExtractor

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        keys = list(self.keys_extractor.extract_records(response))
        values = self.values_extractor.extract_records(response)

        has_more_chunks = True
        while has_more_chunks:
            chunk = [next(values, None) for _ in keys]
            if any(v is None for v in chunk):
                has_more_chunks = False
            else:
                yield dict(zip(keys, chunk))


@dataclass
class DimensionFilterConfigTransformation(RecordTransformation):
    """
    Custom component that takes the incoming config and loops over each custom report and
    transforms the dimensionFilter definition into the format required by the Google Analytics
    API.

    This is not a config migration, but rather an always performed transformation and requires
    a custom component because this is the easiest way to consolidate all the transformation
    logic in one place. The alternative would be a very complex interpolation of the request body.
    """

    def transform(
        self,
        record: MutableMapping[str, Any],
        config: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        for custom_report in record.get("custom_reports_array", []):
            if "dimensionFilter" in custom_report:
                custom_report["dimensionFilter"] = self.transform_dimension_filter(custom_report["dimensionFilter"])

    def transform_dimension_filter(self, dimension_filter: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Performs an in-place transformation of the incoming dimension_filter from our config
        settings into its expected shape according to Google's docs:
        https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/FilterExpression
        """

        transformed_json = {}
        filter_type = dimension_filter.get("filter_type")

        if filter_type in ["andGroup", "orGroup"]:
            expressions = dimension_filter.get("expressions", [])
            transformed_expressions = [self.transform_expression(exp) for exp in expressions]
            transformed_json = {filter_type: {"expressions": transformed_expressions}} if transformed_expressions else {}

        elif filter_type == "notExpression":
            expression = dimension_filter.get("expression")
            transformed_expression = self.transform_expression(expression)
            transformed_json = {filter_type: transformed_expression}

        elif filter_type == "filter":
            transformed_json = self.transform_expression(dimension_filter)

        return transformed_json

    def transform_expression(self, expression: Mapping[str, Any]):
        """
        Performs an in-place transformation of the incoming dimension_filter from our config
        settings into its expected shape according to Google's docs:
        https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/FilterExpression#filter
        """
        transformed_expression = {"fieldName": expression.get("field_name")}
        filter = expression.get("filter")
        filter_name = filter.get("filter_name")

        if filter_name == "stringFilter":
            transformed_expression.update(self.transform_string_filter(filter))
        elif filter_name == "inListFilter":
            transformed_expression.update(self.transform_in_list_filter(filter))
        elif filter_name == "numericFilter":
            transformed_expression.update(self.transform_numeric_filter(filter))
        elif filter_name == "betweenFilter":
            transformed_expression.update(self.transform_between_filter(filter))

        return {"filter": transformed_expression}

    @staticmethod
    def transform_string_filter(filter: Mapping[str, Any]) -> Mapping[str, Any]:
        string_filter = {"value": filter.get("value")}
        if "matchType" in filter:
            string_filter["matchType"] = filter.get("matchType")[0]
        if "caseSensitive" in filter:
            string_filter["caseSensitive"] = filter.get("caseSensitive")
        return {"stringFilter": string_filter}

    @staticmethod
    def transform_in_list_filter(filter: Mapping[str, Any]) -> Mapping[str, Any]:
        in_list_filter = {"values": filter.get("values")}
        if "caseSensitive" in filter:
            in_list_filter["caseSensitive"] = filter.get("caseSensitive")
        return {"inListFilter": in_list_filter}

    @staticmethod
    def transform_numeric_filter(filter: Mapping[str, Any]) -> Mapping[str, Any]:
        numeric_filter = {
            "value": {filter.get("value").get("value_type"): filter.get("value").get("value")},
        }
        if "operation" in filter:
            numeric_filter["operation"] = filter.get("operation")[0]
        return {"numericFilter": numeric_filter}

    @staticmethod
    def transform_between_filter(filter: Mapping[str, Any]) -> Mapping[str, Any]:
        from_value = filter.get("fromValue")
        to_value = filter.get("toValue")

        from_value_type = from_value.get("value_type")
        to_value_type = to_value.get("value_type")

        if from_value_type == "doubleValue" and isinstance(from_value.get("value"), str):
            from_value["value"] = float(from_value.get("value"))
        if to_value_type == "doubleValue" and isinstance(to_value.get("value"), str):
            to_value["value"] = float(to_value.get("value"))

        return {
            "betweenFilter": {
                "fromValue": {from_value_type: from_value.get("value")},
                "toValue": {to_value_type: to_value.get("value")},
            }
        }
