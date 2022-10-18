#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional, Tuple, Dict

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class XkcdStream(HttpStream):
    url_base = "https://xkcd.com"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def path(self, **kwargs) -> str:
        return "/info.0.json"
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        num_records = response.json().get("num")
        for num in range(1, num_records):
            try:
                record = self._get_comic_metadata(num)
            except Exception:
                continue
            yield record
    
    def _get_comic_metadata(self, comic_num: str) -> Dict:
        path = f"https://xkcd.com/{comic_num}/info.0.json"

        request = self._create_prepared_request(
            path=path
        )

        response = self._send_request(request, {})
        return response.json()


class Xkcd(XkcdStream):
    primary_key = None

# Source
class SourceXkcd(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            xkcd = Xkcd()
            xkcd_gen = xkcd.read_records(sync_mode=SyncMode.full_refresh)
            next(xkcd_gen)
            return True, None
        except Exception as error:
            return (
                False,
                f"Unable to connect to XKCD - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Xkcd()]
