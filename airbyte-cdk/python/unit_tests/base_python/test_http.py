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


from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk import SyncMode
from airbyte_cdk.base_python import HttpStream


class StubFullRefreshHttpStream(HttpStream):
    resp_counter = 1
    url_base = "https://test_base_url.com"
    primary_key = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        stubResp = {"data": StubFullRefreshHttpStream.resp_counter}
        StubFullRefreshHttpStream.resp_counter += 1
        yield stubResp


def test_mock_full_refresh_http_stream_read_records(mocker):

    stream = StubFullRefreshHttpStream()
    blank_response = {}  # Send a blank response is fine as we ignore the response in `parse_response anyway.
    mocker.patch.object(StubFullRefreshHttpStream, "_send_request", return_value=blank_response)

    records = []
    for r in stream.read_records(SyncMode.full_refresh):
        records.append(r)

    assert [ {"data": 1} ] == records

# test_incremental_stream_read_records


# test back_off_for_stream
