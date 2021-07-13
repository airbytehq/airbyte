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
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class ConversationExport(HttpStream, ABC):
    url_base = "https://exports.dixa.io/v1/"
    primary_key = "id"
    cursor_field = "updated_at"

    def __init__(self, start_date: datetime, batch_size: int, logger: AirbyteLogger, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_date = start_date
        self.start_timestamp = ConversationExport.datetime_to_ms_timestamp(self.start_date)
        # The upper bound is exclusive.
        self.end_timestamp = ConversationExport.datetime_to_ms_timestamp(datetime.now()) + 1
        self.batch_size = batch_size
        self.logger = logger

    @staticmethod
    def _validate_ms_timestamp(milliseconds: int) -> int:
        if not type(milliseconds) == int or not len(str(milliseconds)) == 13:
            raise ValueError(f"Not a millisecond-precision timestamp: {milliseconds}")
        return milliseconds

    @staticmethod
    def ms_timestamp_to_datetime(milliseconds: int) -> datetime:
        """
        Converts a millisecond-precision timestamp to a datetime object.
        """
        return datetime.fromtimestamp(ConversationExport._validate_ms_timestamp(milliseconds) / 1000, tz=timezone.utc)

    @staticmethod
    def datetime_to_ms_timestamp(dt: datetime) -> int:
        """
        Converts a datetime object to a millisecond-precision timestamp.
        """
        return int(dt.timestamp() * 1000)

    @staticmethod
    def add_days_to_ms_timestamp(days: int, milliseconds: int) -> int:
        return ConversationExport.datetime_to_ms_timestamp(
            ConversationExport.ms_timestamp_to_datetime(ConversationExport._validate_ms_timestamp(milliseconds)) + timedelta(days=days)
        )

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        self.logger.info(
            f"Sending request with updated_after={stream_slice['updated_after']} and " f"updated_before={stream_slice['updated_before']}"
        )
        return stream_slice

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    def backoff_time(self, response: requests.Response):
        """
        The rate limit is 10 requests per minute, so we sleep for one minute
        once we have reached 10 requests.

        See https://support.dixa.help/en/articles/174-export-conversations-via-api
        """
        return 60

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs):
        """
        Returns slices of size self.batch_size.
        """
        slices = []

        stream_state = stream_state or {}
        # If stream_state contains the cursor field and the value of the cursor
        # field is higher than start_timestamp, then start at the cursor field
        # value. Otherwise, start at start_timestamp.
        updated_after = max(stream_state.get(ConversationExport.cursor_field, 0), self.start_timestamp)
        while updated_after < self.end_timestamp:
            updated_before = min(
                ConversationExport.add_days_to_ms_timestamp(days=self.batch_size, milliseconds=updated_after), self.end_timestamp
            )
            slices.append({"updated_after": updated_after, "updated_before": updated_before})
            updated_after = updated_before
        return slices

    def path(self, **kwargs) -> str:
        return "conversation_export"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        Uses the `updated_at` field, which is a Unix timestamp with millisecond precision.
        """
        if current_stream_state is not None and ConversationExport.cursor_field in current_stream_state:
            return {
                ConversationExport.cursor_field: max(
                    current_stream_state[ConversationExport.cursor_field], latest_record[ConversationExport.cursor_field]
                )
            }
        else:
            return {ConversationExport.cursor_field: self.start_timestamp}


class SourceDixa(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Try loading one day's worth of data.
        """
        try:
            start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
            start_timestamp = ConversationExport.datetime_to_ms_timestamp(start_date)
            url = "https://exports.dixa.io/v1/conversation_export"
            headers = {"accept": "application/json"}
            response = requests.request(
                "GET",
                url=url,
                headers=headers,
                params={
                    "updated_after": start_timestamp,
                    "updated_before": ConversationExport.add_days_to_ms_timestamp(days=1, milliseconds=start_timestamp),
                },
                auth=("bearer", config["api_token"]),
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_token"])
        return [
            ConversationExport(
                authenticator=auth,
                start_date=datetime.strptime(config["start_date"], "%Y-%m-%d"),
                batch_size=int(config["batch_size"]),
                logger=AirbyteLogger(),
            )
        ]
