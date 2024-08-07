#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass

import requests
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class EventsRecordExtractor(DpathExtractor):
    def extract_records(self, response: requests.Response) -> list[Record]:
        response_body = self.decoder.decode(response)
        events = response_body.get("events")
        if events:
            return [{"event_name": value} for value in events]
        else:
            return []
