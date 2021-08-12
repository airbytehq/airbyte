#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from . import utils


class DixaStream(HttpStream, ABC):

    primary_key = "id"
    url_base = "https://exports.dixa.io/v1/"

    backoff_sleep = 60  # seconds

    def __init__(self, config: Mapping[str, Any]) -> None:
        super().__init__(authenticator=config["authenticator"])
        self.start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        self.start_timestamp = utils.datetime_to_ms_timestamp(self.start_date)
        self.end_timestamp = utils.datetime_to_ms_timestamp(datetime.now()) + 1
        self.batch_size = config["batch_size"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def backoff_time(self, response: requests.Response):
        """
        The rate limit is 10 requests per minute, so we sleep for one minute
        once we have reached 10 requests.

        See https://support.dixa.help/en/articles/174-export-conversations-via-api
        """
        return self.backoff_sleep


class IncrementalDixaStream(DixaStream):

    cursor_field = "updated_at"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        self.logger.info(
            f"Sending request with updated_after={stream_slice['updated_after']} and " f"updated_before={stream_slice['updated_before']}"
        )
        return stream_slice

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        Uses the `updated_at` field, which is a Unix timestamp with millisecond precision.
        """
        current_stream_state = current_stream_state or {}
        return {self.cursor_field: max(current_stream_state.get(self.cursor_field, 0), latest_record.get(self.cursor_field, 0))}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs):
        """
        Returns slices of size self.batch_size
        """
        slices = []

        stream_state = stream_state or {}
        # If stream_state contains the cursor field and the value of the cursor
        # field is higher than start_timestamp, then start at the cursor field
        # value. Otherwise, start at start_timestamp.
        updated_after = max(stream_state.get(self.cursor_field, 0), self.start_timestamp)
        while updated_after < self.end_timestamp:
            updated_before = min(utils.add_days_to_ms_timestamp(days=self.batch_size, milliseconds=updated_after), self.end_timestamp)
            slices.append({"updated_after": updated_after, "updated_before": updated_before})
            updated_after = updated_before
        return slices


class ConversationExport(IncrementalDixaStream):
    def path(self, **kwargs) -> str:
        return "conversation_export"


class SourceDixa(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Check connectivity using one day's worth of data.
        """
        auth = TokenAuthenticator(token=config["api_token"]).get_auth_header()
        url = "https://exports.dixa.io/v1/conversation_export"
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        start_timestamp = utils.datetime_to_ms_timestamp(start_date)
        params = {
            "updated_after": start_timestamp,
            "updated_before": utils.add_days_to_ms_timestamp(days=1, milliseconds=start_timestamp),
        }

        try:
            response = requests.get(url=url, headers=auth, params=params)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = TokenAuthenticator(token=config["api_token"])
        return [
            ConversationExport(config),
        ]
