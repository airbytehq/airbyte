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
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


DATE_FORMAT = "%Y-%m-%d"


class DixaStream(HttpStream, ABC):
    url_base = "https://exports.dixa.io/v1/"
    date_format = DATE_FORMAT

    def __init__(self, start_date: date, batch_size: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_date = start_date
        self.batch_size = batch_size

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
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

    def stream_slices(self, **kwargs):
        """
        Break down the days between start_date and the current date into
        chunks.
        """
        end_date = datetime.now().date()
        created_after = self.start_date
        created_before = min(
            created_after + timedelta(days=self.batch_size),
            end_date
        )
        slices = [{
            'created_after': created_after,
            'created_before': created_before
        }]
        while created_after < end_date:
            created_after = created_before
            created_before = min(
                created_after + timedelta(days=self.batch_size),
                end_date
            )
            slices.append({
                'created_after': created_after,
                'created_before': created_before
            })
        return slices


class ConversationExport(DixaStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "conversation_export"


class SourceDixa(AbstractSource):
    date_format = DATE_FORMAT

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Try loading one day's worth of data.
        """
        try:
            url = "https://exports.dixa.io/v1/conversation_export"
            headers = {'accept': 'application/json'}
            response = requests.request(
                'GET',
                url=url,
                headers=headers,
                params={
                    "created_after": config["start_date"],
                    "created_before": (
                        datetime.strptime(
                            config["start_date"], SourceDixa.date_format
                        ) + timedelta(days=config["batch_size"])
                    ).strftime(SourceDixa.date_format)
                },
                auth=('bearer', config["api_token"])
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
                batch_size=config["batch_size"]
            )
        ]
