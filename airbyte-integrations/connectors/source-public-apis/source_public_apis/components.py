#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from typing import Any

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


class CustomExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response, **kwargs) -> list[Mapping[str, Any]]:
        return [{"name": cat} for cat in response.json()["categories"]]
