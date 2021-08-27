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
import pytest
import responses
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_slack.source import SlackStream


class MockSlackStream(SlackStream):
    def path(self, **kwargs) -> str:
        return "dummmy/path"

    data_field = "dummy_data_field"


@responses.activate
def test_slack_stream_backoff_500(mocker):
    mocker.patch("time.sleep", return_value=None)
    responses.add(responses.GET, "https://slack.com/api/dummmy/path", json={}, status=500)
    slack_stream = MockSlackStream()

    with pytest.raises(HTTPError):
        [r for r in slack_stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(responses.calls) == slack_stream.max_retry_attempts + 1
    responses.reset()

    # Send this request one more time to make sure retry attempts has been reseted
    responses.add(responses.GET, "https://slack.com/api/dummmy/path", json={}, status=500)
    with pytest.raises(HTTPError):
        [r for r in slack_stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert len(responses.calls) == slack_stream.max_retry_attempts + 1


@responses.activate
def test_slack_stream_backoff_429(mocker):
    sleep_mock = mocker.patch("time.sleep", return_value=None)
    retry_slack_response = 1
    infinite_number = 20

    class ResponseCB:
        current_retries = 0

        def __call__(self, request):
            self.current_retries += 1
            if self.current_retries > infinite_number:
                raise Exception("Infinite number reached")
            return (429, {"Retry-After": str(retry_slack_response)}, "{}")

    responses.add_callback(responses.GET, "https://slack.com/api/dummmy/path", callback=ResponseCB())
    slack_stream = MockSlackStream()

    with pytest.raises(Exception) as ex_info:
        [r for r in slack_stream.read_records(sync_mode=SyncMode.full_refresh)]
    assert str(ex_info.value) == "Infinite number reached"
    sleep_args = [call[0][0] for call in sleep_mock.call_args_list]
    assert all([arg == retry_slack_response + 1 for arg in sleep_args if arg])
    assert len(responses.calls) == infinite_number + 1
