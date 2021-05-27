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


import unittest

from unittest.mock import patch

from source_http_request import SourceHttpRequest


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class TestSourceHttpRequest(unittest.TestCase):
    def test_parse_config(self):
        config = {
            "http_method": "get",
            "url": "http://api.bart.gov/api",
            "headers": '{"Content-Type": "application/json"}',
            "body": '{"something": "good"}',
        }

        source = SourceHttpRequest()
        actual = source._parse_config(config)
        expected = {
            "http_method": "get",
            "url": "http://api.bart.gov/api",
            "headers": {"Content-Type": "application/json"},
            "body": {"something": "good"},
        }
        self.assertEqual(expected, actual)

    def test_json_array_response(self):
        with patch.object(
            SourceHttpRequest,
            attribute="_make_request",
            return_value=MockResponse(
                json_data=[
                    ["foo", "bar"],
                    ["test", 10],
                    ["test2", 15],
                ],
                status_code=200,
            ),
        ):
            expected = [
                {"data": ["foo", "bar"]},
                {"data": ["test", "10"]},
                {"data": ["test2", "15"]},
            ]
            source = SourceHttpRequest()
            results = [
                r.record.data
                for r in list(
                    source.read(
                        logger=None,
                        state=None,
                        catalog=None,
                        config={},
                    )
                )
            ]
            self.assertEqual(expected, results)
