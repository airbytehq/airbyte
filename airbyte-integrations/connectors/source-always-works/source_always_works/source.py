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


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class AlwaysWorksStream(HttpStream):

    current_counter = 0  # Counter for current response number.
    url_base = "stub_base"
    primary_key = "stub_key"

    def __init__(self, limit: int):
        super().__init__()
        self._limit = limit

    # Ignored Functions
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "unused"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    # Used Functions
    def read_records(
        self,
        sync_mode: SyncMode,
        stream_state: Mapping[str, Any] = None,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Override this to only call the parse_response function.
        """
        return self.parse_response(requests.Response())

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Return the self._limit number of slices, so the same number of read_record
        calls are made.
        """
        for i in range(self._limit):
            yield i

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Returns an incrementing number.
        """
        self.current_counter += 1
        yield {"count": self.current_counter}


class SourceAlwaysWorks(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Always works is always working; return True
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [AlwaysWorksStream(config["limit"])]
