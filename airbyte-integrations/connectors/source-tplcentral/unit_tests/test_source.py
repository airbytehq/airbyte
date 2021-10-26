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

from pytest import fixture
from source_tplcentral.source import SourceTplcentral


@fixture
def config():
    return {
        "config": {
            "url_base": "https://secure-wms.com/",
            "client_id": "xxx",
            "client_secret": "yyy",
            "user_login_id": 123,
            "tpl_key": "{00000000-0000-0000-0000-000000000000}",
            "customer_id": 4,
            "facility_id": 5,
            "start_date": "2021-10-01"
        }
    }


def test_check_connection(mocker, requests_mock, config):
    source = SourceTplcentral()
    logger_mock = MagicMock()
    requests_mock.post(
        f"{config['config']['url_base']}AuthServer/api/Token",
        json={
            "access_token": "the_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": None,
            "scope": None,
        },
    )
    assert source.check_connection(logger_mock, **config) == (True, None)


def test_streams(mocker):
    source = SourceTplcentral()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 6
    assert len(streams) == expected_streams_number
