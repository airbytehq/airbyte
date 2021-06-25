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
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


DATE_FORMAT = "%Y-%m-%d"


# Basic full refresh stream
class DixaStream(HttpStream, ABC):
    url_base = "https://exports.dixa.io/v1/"
    date_format = DATE_FORMAT

    def __init__(self, start_date: datetime, **kwargs) -> None:
        super().__init__(**kwargs)
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            'created_after': self.start_date.strftime(DixaStream.date_format),
            'created_before': (
                self.start_date + timedelta(days=1)
            ).strftime(DixaStream.date_format)
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


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
                        ) + timedelta(days=1)
                    ).strftime(SourceDixa.date_format)
                },
                auth=('bearer', config["api_key"])
            )
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        start_date = datetime.strptime(config["start_date"], SourceDixa.date_format)
        auth = TokenAuthenticator(token=config["api_key"])
        return [ConversationExport(authenticator=auth, start_date=start_date)]
