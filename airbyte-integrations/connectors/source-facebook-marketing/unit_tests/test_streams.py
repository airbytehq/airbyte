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

from source_facebook_marketing.streams import remove_params_from_url


class TestUrlParsing:
    def test_empty_url(self):
        url = ""
        parsed_url = remove_params_from_url(url=url, params=[])
        assert parsed_url == url

    def test_does_not_raise_exception_for_invalid_url(self):
        url = "abcd"
        parsed_url = remove_params_from_url(url=url, params=["test"])
        assert parsed_url == url

    def test_escaped_characters(self):
        url = "https://google.com?test=123%23%24%25%2A&test2=456"
        parsed_url = remove_params_from_url(url=url, params=["test3"])
        assert parsed_url == url

    def test_no_params_url(self):
        url = "https://google.com"
        parsed_url = remove_params_from_url(url=url, params=["test"])
        assert parsed_url == url

    def test_no_params_arg(self):
        url = "https://google.com?"
        parsed_url = remove_params_from_url(url=url, params=["test"])
        assert parsed_url == "https://google.com"

    def test_partially_empty_params(self):
        url = "https://google.com?test=122&&"
        parsed_url = remove_params_from_url(url=url, params=[])
        assert parsed_url == "https://google.com?test=122"

    def test_no_matching_params(self):
        url = "https://google.com?test=123"
        parsed_url = remove_params_from_url(url=url, params=["test2"])
        assert parsed_url == url

    def test_removes_params(self):
        url = "https://google.com?test=123&test2=456"
        parsed_url = remove_params_from_url(url=url, params=["test2"])
        assert parsed_url == "https://google.com?test=123"
