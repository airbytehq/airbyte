#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Any, List, Mapping, Union

import dpath.util
import requests

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record


logger = logging.getLogger("airbyte")


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
        if not response_body["data"]["boards"]:
            return result

        for board_data in response_body["data"]["boards"]:
            if not isinstance(board_data, dict) or not board_data.get("activity_logs"):
                continue
            for record in board_data.get("activity_logs", []):
                json_data = json.loads(record["data"])
                new_record = record
                if record.get("created_at"):
                    new_record.update({"created_at_int": int(record.get("created_at", 0)) // 10_000_000})
                else:
                    continue

                if record.get("entity") == "pulse" and json_data.get("pulse_id"):
                    new_record.update({"pulse_id": json_data.get("pulse_id")})

                if record.get("entity") == "board" and json_data.get("board_id"):
                    new_record.update({"board_id": json_data.get("board_id")})

                result.append(new_record)

        return result


@dataclass
class MondayIncrementalItemsExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    field_path_pagination: List[Union[InterpolatedString, str]] = field(default_factory=list)
    field_path_incremental: List[Union[InterpolatedString, str]] = field(default_factory=list)
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for field_list in (self.field_path, self.field_path_pagination, self.field_path_incremental):
            for path_index in range(len(field_list)):
                if isinstance(field_list[path_index], str):
                    field_list[path_index] = InterpolatedString.create(field_list[path_index], parameters=parameters)

    def try_extract_records(self, response: requests.Response, field_path: List[Union[InterpolatedString, str]]) -> List[Record]:
        response_body = self.decoder.decode(response)

        path = [path.eval(self.config) for path in field_path]
        extracted = dpath.util.values(response_body, path) if path else response_body

        pattern_path = "*" in path
        if not pattern_path:
            extracted = dpath.util.get(response_body, path, default=[])

        if extracted:
            if isinstance(extracted, list) and None in extracted:
                logger.warning(f"Record with null value received; errors: {response_body.get('errors')}")
                return [x for x in extracted if x]
            return extracted if isinstance(extracted, list) else [extracted]
        return []

    def extract_records(self, response: requests.Response) -> List[Record]:
        result = self.try_extract_records(response, field_path=self.field_path)
        if not result and self.field_path_pagination:
            result = self.try_extract_records(response, self.field_path_pagination)
        if not result and self.field_path_incremental:
            result = self.try_extract_records(response, self.field_path_incremental)

        for record in result:
            if "updated_at" in record:
                record["updated_at_int"] = int(datetime.strptime(record["updated_at"], "%Y-%m-%dT%H:%M:%S%z").timestamp())

            column_values = record.get("column_values", [])
            for values in column_values:
                display_value, text = values.get("display_value"), values.get("text")
                if display_value and not text:
                    values["text"] = display_value

        return result
