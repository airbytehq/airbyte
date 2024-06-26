# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import List

import requests
from airbyte_cdk.sources.declarative.extractors import DpathExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class ChannelMembersExtractor(DpathExtractor):
    """
    Transform response from list of strings to list dicts:
    from: ['aa', 'bb']
    to: [{'member_id': 'aa'}, {{'member_id': 'bb'}]
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        records = super().extract_records(response)
        return [{"member_id": record} for record in records]
