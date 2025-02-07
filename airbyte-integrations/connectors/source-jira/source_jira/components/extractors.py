# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, List, Mapping

from requests_cache import Response

from airbyte_cdk.sources.declarative.extractors import DpathExtractor


@dataclass
class LabelsRecordExtractor(DpathExtractor):
    """
    A custom record extractor is needed to handle cases when records are represented as list of strings insted of dictionaries.
    Example:
        -> ["label 1", "label 2", ..., "label n"]
        <- [{"label": "label 1"}, {"label": "label 2"}, ..., {"label": "label n"}]
    """

    def extract_records(self, response: Response) -> List[Mapping[str, Any]]:
        records = super().extract_records(response)
        return [{"label": record} for record in records]
