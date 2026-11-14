#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Iterable, Mapping, MutableMapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class IndicatorCatalogueExtractor(RecordExtractor):
    """
    Extracts records from a /v1/data_catalogue/{currency} response, which is an
    object keyed by indicator slug:

    { "gdp": { "name": "GDP", ... }, "inflation": { "name": "CPI", ... } }

    Each entry is emitted as its own record with the slug added as `indicator`.
    """

    parameters: InitVar[Mapping[str, Any]]

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        body = response.json()
        if not isinstance(body, dict):
            return
        for indicator, entry in body.items():
            if isinstance(entry, dict):
                yield {"indicator": indicator, **entry}
