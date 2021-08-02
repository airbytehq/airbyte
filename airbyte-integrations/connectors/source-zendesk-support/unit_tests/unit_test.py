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

import json
from unittest import TestCase

import requests_mock
import timeout_decorator
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException
from source_zendesk_support import SourceZendeskSupport
from source_zendesk_support.streams import Tags

CONFIG_FILE = "secrets/config.json"


class TestZendeskSupport(TestCase):
    """This test class provides a set of tests for different Zendesk streams.
    The Zendesk API has difference pagination and sorting mechanisms for streams.
    Let's try to check them
    """

    @staticmethod
    def prepare_stream_args():
        """Generates streams settings from a file"""
        with open(CONFIG_FILE, "r") as f:
            return SourceZendeskSupport.convert_config2stream_args(json.loads(f.read()))

    @timeout_decorator.timeout(10)
    def test_backoff(self):
        """Zendesk sends the header 'Retry-After' about needed delay.
        All streams have to handle it"""
        timeout = 1
        stream = Tags(**self.prepare_stream_args())
        with requests_mock.Mocker() as m:
            url = stream.url_base + stream.path()
            m.get(url, text=json.dumps({}), status_code=429, headers={"Retry-After": str(timeout)})
            with self.assertRaises(UserDefinedBackoffException):
                list(stream.read_records(sync_mode=None))
