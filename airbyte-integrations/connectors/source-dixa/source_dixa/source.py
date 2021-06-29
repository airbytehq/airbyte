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


from abc import ABC
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


DATE_FORMAT = "%Y-%m-%d"


class DixaStream(HttpStream, ABC):
    url_base = "https://exports.dixa.io/v1/"
    date_format = DATE_FORMAT

    def __init__(self, start_date: date, batch_size: int, logger: AirbyteLogger, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_date = start_date
        self.batch_size = batch_size
        self.logger = logger

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        self.logger.info(
            f"Sending request with updated_after={stream_slice['updated_after']} and "
            f"updated_before={stream_slice['updated_before']}"
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
        Break down the days between start_date and the current date into
        chunks.
        """
        end_date = datetime.now().date()
        updated_after = datetime.strptime(
            stream_state["date"], "%Y-%m-%d"
        ).date() if stream_state and "date" in stream_state else self.start_date
        updated_before = min(
            updated_after + timedelta(days=self.batch_size),
            end_date
        )
        slices = [{
            "updated_after": updated_after,
            "updated_before": updated_before
        }]
        while updated_after < end_date:
            updated_after = updated_before
            updated_before = min(
                updated_after + timedelta(days=self.batch_size),
                end_date
            )
            slices.append({
                "updated_after": updated_after,
                "updated_before": updated_before
            })
        return slices


class ConversationExport(DixaStream):
    primary_key = "id"
    cursor_field = "updated_at"

    def path(
        self, **kwargs
    ) -> str:
        return "conversation_export"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        Uses the date from the `updated_at` field, which is a Unix timestamp with millisecond precision.
        """
        if current_stream_state is not None and 'date' in current_stream_state:
            current_state_value = datetime.strptime(current_stream_state["date"], "%Y-%m-%d").date()
            # Divide millisecond-precision timestamp by 1000 to get second-precision timestamp
            latest_record_value = datetime.fromtimestamp(latest_record[ConversationExport.cursor_field]//1000).date()
            return {'date': max(current_state_value, latest_record_value).strftime("%Y-%m-%d")}
        else:
            return {'date': self.start_date.strftime("%Y-%m-%d")}


class SourceDixa(AbstractSource):
    date_format = DATE_FORMAT

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Try loading one day's worth of data.
        """
        try:
            url = "https://exports.dixa.io/v1/conversation_export"
            headers = {"accept": "application/json"}
            response = requests.request(
                "GET",
                url=url,
                headers=headers,
                params={
                    "updated_after": config["start_date"],
                    "updated_before": (
                        datetime.strptime(
                            config["start_date"], SourceDixa.date_format
                        ) + timedelta(days=1)
                    ).strftime(SourceDixa.date_format)
                },
                auth=("bearer", config["api_token"])
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        start_date = datetime.strptime(config["start_date"], SourceDixa.date_format).date()
        auth = TokenAuthenticator(token=config["api_token"])
        return [
            ConversationExport(
                authenticator=auth,
                start_date=start_date,
                batch_size=int(config["batch_size"]),
                logger=AirbyteLogger()
            )
        ]
