#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from dataclasses import dataclass
from io import StringIO

import requests
from typing import Iterable
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState


@dataclass
class XJsonRecordExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> list[Record]:
        for record in response.iter_lines():
            yield json.loads(record)


@dataclass
class ListUsersRecordExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Record]:
        for record in response.iter_lines():
            yield {"email": record.decode()}


@dataclass
class EventsRecordExtractor(DpathExtractor):
    common_fields = ("itblInternal", "_type", "createdAt", "email")

    def extract_records(self, response: requests.Response) -> Iterable[Record]:
        jsonl_records = StringIO(response.text)
        for record in jsonl_records:
            record_dict = json.loads(record)
            record_dict_common_fields = {}
            for field in self.common_fields:
                record_dict_common_fields[field] = record_dict.pop(field, None)
            yield {**record_dict_common_fields, "data": record_dict}
