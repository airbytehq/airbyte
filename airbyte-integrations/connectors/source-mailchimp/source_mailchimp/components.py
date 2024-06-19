# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, Mapping

import requests
from airbyte_cdk.sources.declarative.extractors import DpathExtractor


class MailChimpRecordExtractorEmailActivity(DpathExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        records = super().extract_records(response=response)
        yield from ({**record, **activity_item} for record in records for activity_item in record.pop("activity", []))
