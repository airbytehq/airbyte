#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping

import requests

from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


date_time_parser = DatetimeParser()


@dataclass
class ZendeskChatBansRecordExtractor(RecordExtractor):
    """
    Unnesting nested bans: `visitor`, `ip_address`.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> Iterable[Mapping[str, Any]]:
        response_data = response.json()
        ip_address: List[Mapping[str, Any]] = response_data.get("ip_address", [])
        visitor: List[Mapping[str, Any]] = response_data.get("visitor", [])
        bans = ip_address + visitor
        bans = sorted(
            bans,
            key=lambda x: date_time_parser.parse(date=x["created_at"], format="%Y-%m-%dT%H:%M:%SZ")
            if x["created_at"]
            else date_time_parser.parse(date=DatetimeParser._UNIX_EPOCH, format="%Y-%m-%dT%H:%M:%SZ"),
        )
        yield from bans
