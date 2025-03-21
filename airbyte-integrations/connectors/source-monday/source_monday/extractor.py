#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Union

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

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        response_body_generator = self.decoder.decode(response)
        for response_body in response_body_generator:
            if not response_body["data"]["boards"]:
                continue

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

                    yield new_record


@dataclass
class MondayIncrementalItemsExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    field_path_pagination: List[Union[InterpolatedString, str]] = field(default_factory=list)
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        # Convert string paths to InterpolatedString for both field_path and field_path_pagination
        self._field_path = [
            InterpolatedString.create(p, parameters=parameters) if isinstance(p, str) else p
            for p in self.field_path
        ]
        self._field_path_pagination = [
            InterpolatedString.create(p, parameters=parameters) if isinstance(p, str) else p
            for p in self.field_path_pagination
        ]

    def _try_extract_records(self, response: requests.Response, field_path: List[Union[InterpolatedString, str]]) -> Iterable[Mapping[str, Any]]:
        for body in self.decoder.decode(response):
            if len(field_path) == 0:
                extracted = body
            else:
                path = [p.eval(self.config) for p in field_path]
                if "*" in path:
                    extracted = dpath.values(body, path)
                else:
                    extracted = dpath.get(body, path, default=[])

            if extracted:
                if isinstance(extracted, list) and None in extracted:
                    logger.warning(f"Record with null value received; errors: {body.get('errors')}")
                    yield from (x for x in extracted if x)
                else:
                    yield from extracted if isinstance(extracted, list) else [extracted]

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        # Try primary field path
        has_records = False
        for record in self._try_extract_records(response, self._field_path):
            has_records = True
            yield record

        # Fallback to pagination path if no records and path exists
        if not has_records and self._field_path_pagination:
            yield from self._try_extract_records(response, self._field_path_pagination)
