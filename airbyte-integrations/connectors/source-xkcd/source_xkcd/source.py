#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class XkcdStream(HttpStream):
    url_base = "https://xkcd.com"
    last_comic = 0
    comic_number = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs: Any) -> str:
        if next_page_token:
            next_token: str = next_page_token["next_token"]
            return f"/{next_token}/info.0.json"
        return "/info.0.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.last_comic < response.json().get("num"):
            self.last_comic = response.json().get("num")
        # There is not a comic 404
        if self.comic_number == 403:
            self.comic_number = 405
        if self.comic_number < self.last_comic:
            self.comic_number = self.comic_number + 1
            return {"next_token": self.comic_number}
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        record = response.json()
        yield record


class Xkcd(XkcdStream):
    primary_key = "num"


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
