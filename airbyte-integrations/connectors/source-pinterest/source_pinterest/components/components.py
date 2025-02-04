#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import List

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Config, Record


class AdAccountRecordExtractor(RecordExtractor):
    """
    Custom extractor for handling different response formats from the Ad Accounts endpoint.

    This extractor is necessary to handle cases where an `account_id` is present in the request.
    - When querying all ad accounts, the response contains an "items" key with a list of accounts.
    - When querying a specific ad account, the response returns a single dictionary representing that account.
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        data = response.json()

        if not data:
            return []

        # Extract records from "items" if present
        if isinstance(data, dict) and "items" in data:
            return data["items"]

        # If the response is a single object, wrap it in a list
        if isinstance(data, dict):
            return [data]
        return []
