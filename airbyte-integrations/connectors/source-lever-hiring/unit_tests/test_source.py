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

from unittest.mock import MagicMock

import responses
from source_lever_hiring.source import SourceLeverHiring


def setup_responses():
    responses.add(
        responses.POST,
        "https://sandbox-lever.auth0.com/oauth/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourceLeverHiring()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


@responses.activate
def test_streams(test_config):
    setup_responses()
    source = SourceLeverHiring()
    streams = source.streams(test_config)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number
