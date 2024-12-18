#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import InitVar, dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config


class ParseDates:
    @staticmethod
    def parse_date(value):
        # Xero datetimes can be .NET JSON date strings which look like
        # "/Date(1419937200000+0000)/"
        # https://developer.xero.com/documentation/api/requests-and-responses
        pattern = r"Date\((\-?\d+)([-+])?(\d+)?\)"
        match = re.search(pattern, value)
        iso8601pattern = r"((\d{4})-([0-2]\d)-0?([0-3]\d)T([0-5]\d):([0-5]\d):([0-6]\d))"
        if not match:
            iso8601match = re.search(iso8601pattern, value)
            if iso8601match:
                try:
                    return datetime.strptime(value)
                except Exception:
                    return None
            else:
                return None

        millis_timestamp, offset_sign, offset = match.groups()
        if offset:
            if offset_sign == "+":
                offset_sign = 1
            else:
                offset_sign = -1
            offset_hours = offset_sign * int(offset[:2])
            offset_minutes = offset_sign * int(offset[2:])
        else:
            offset_hours = 0
            offset_minutes = 0

        return datetime.fromtimestamp((int(millis_timestamp) / 1000), tz=timezone.utc) + timedelta(
            hours=offset_hours, minutes=offset_minutes
        )

    @staticmethod
    def convert_dates(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    parsed_value = ParseDates.parse_date(value)
                    if parsed_value:
                        if isinstance(parsed_value, date):
                            parsed_value = datetime.combine(parsed_value, time.min)
                        parsed_value = parsed_value.replace(tzinfo=timezone.utc)
                        obj[key] = datetime.isoformat(parsed_value, timespec="seconds")
                elif isinstance(value, (dict, list)):
                    ParseDates.convert_dates(value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], (dict, list)):
                    ParseDates.convert_dates(obj[i])


@dataclass
class CustomExtractor(RecordExtractor):
    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self.field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        response_body = self.decoder.decode(response)
        if len(self.field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in self.field_path]
            if "*" in path:
                extracted = dpath.util.values(response_body, path)
            else:
                extracted = dpath.util.get(response_body, path, default=[])

        ParseDates.convert_dates(extracted)

        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []
