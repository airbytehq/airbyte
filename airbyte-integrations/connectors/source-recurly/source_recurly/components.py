# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


class ExportDatesExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            dates = response.json()["dates"]
        except requests.exceptions.JSONDecodeError:
            dates = []
        return [{"dates": dates}]
