#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


logger = logging.getLogger("airbyte")


class AccessibleAccountsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        response_data = response.json().get("resourceNames", [])
        if response_data:
            for resource_name in response_data:
                yield {"accessible_customer_id": resource_name.split("/")[-1]}
