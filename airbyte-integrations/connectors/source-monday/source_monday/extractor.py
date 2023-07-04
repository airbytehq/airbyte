#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record


@dataclass
class MondayActivityExtractor(RecordExtractor):
    """
    Record extractor that extracts record of the form from activity logs stream:

    { "list": { "ID_1": record_1, "ID_2": record_2, ... } }

    Attributes:
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        result = []
        if len(response_body["data"]["boards"]):
            for record in response_body["data"]["boards"][0]["activity_logs"]:
                json_data = json.loads(record["data"])
                if json_data.get("pulse_id"):
                    result.append(
                        dict(
                            record,
                            **{"pulse_id": json_data.get("pulse_id"), "created_at_int": int(record.get("created_at", 0)) // 10_000_000},
                        )
                    )
        return result


@dataclass
class MondayItemsExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.
    """

    field_path: List[Union[InterpolatedString, str]]
    additional_field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for field in (self.field_path, self.additional_field_path):
            for path_index in range(len(field)):
                if isinstance(field[path_index], str):
                    field[path_index] = InterpolatedString.create(field[path_index], parameters=parameters)

    def try_extract_records(self, response: requests.Response, field_path: List[Union[InterpolatedString, str]]) -> List[Record]:
        response_body = self.decoder.decode(response)
        if len(field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in field_path]
            if "*" in path:
                extracted = dpath.util.values(response_body, path)
            else:
                extracted = dpath.util.get(response_body, path, default=[])
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []

    def extract_records(self, response: requests.Response) -> List[Record]:
        default_path_records = self.try_extract_records(response, field_path=self.field_path)
        if not default_path_records:
            return self.try_extract_records(response, self.additional_field_path)
        return default_path_records
