#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class XingStream(HttpStream, ABC):

    url_base = "https://api.xing.com/vendor/ad-manager-api/v1/"

    def __init__(self, config: Mapping[str, Any], authenticator, parent):
        super().__init__(parent)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("next_page")
        if next_page is not None:
            return {"next_page": next_page}
        else:
            return None

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        if response.status_code == 200:
            for x in response.json().get("data"):
                x["customer_id"] = stream_slice["customer_id"]
                yield x

    def backoff_time(
        self,
        response: requests.Response,
    ) -> Optional[float]:
        """Xing has a rather low request limit:
        120/60sec
        1200/60min
        15000/24h
        Retrying will start after the ban_time that is part of the response.
        Docs: https://dev.xing.com/docs/rate_limits"""
        if response.json().get("error_name") == "RATE_LIMIT_EXCEEDED":
            self.logger.info(response.json().get("message"), "Sleeping for: ", response.json().get("ban_time"))
            return float(response.json().get("ban_time", 0))
        else:
            self.logger.info("Using default backoff value.")
            return 60

    def should_retry(self, response: requests.Response) -> bool:
        return response.status_code in (403, 429, 500)


class IncrementalXingStream(XingStream, ABC):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}
