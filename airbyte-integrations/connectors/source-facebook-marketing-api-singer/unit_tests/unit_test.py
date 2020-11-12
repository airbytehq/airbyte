"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from base_python import AirbyteLogger
from source_facebook_marketing_api_singer import SourceFacebookMarketingApiSinger

LOGGER = AirbyteLogger()
CONNECTOR = SourceFacebookMarketingApiSinger()
FAKE_CONFIG_PATH = "/tmp/config"
FAKE_CATALOG_PATH = "/tmp/catalog"


def test_discover_cmd():
    cmd = CONNECTOR.discover_cmd(LOGGER, FAKE_CONFIG_PATH)
    assert f"tap-facebook -c {FAKE_CONFIG_PATH} --discover" == cmd.strip()


def test_read_cmd():
    cmd = CONNECTOR.read_cmd(LOGGER, FAKE_CONFIG_PATH, FAKE_CATALOG_PATH)
    assert f"tap-facebook -c {FAKE_CONFIG_PATH} -p {FAKE_CATALOG_PATH}" == cmd.strip()


def test_transform_config_adds_include_deleted_sandbox_if_empty():
    input = {
        "start_date": "start_date",
        "account_id": "account_id",
        "access_token": "access_token",
    }
    expected = dict(input)
    expected["include_deleted"] = "True"
    assert expected == CONNECTOR.transform_config(input)
