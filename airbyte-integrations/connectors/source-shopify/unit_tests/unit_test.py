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

import requests
from source_shopify.source import ShopifyStream


def test_get_next_page_token(requests_mock):
    """
    Test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call,
    """
    response_header_links = {
        "Date": "Thu, 32 Jun 2099 24:24:24 GMT",
        "Content-Type": "application/json; charset=utf-8",
        "Link": '<https://test_shop.myshopify.com/admin/api/2021-04/test_object.json?limit=1&page_info=eyJjcmVhdGVkX2>; rel="next"',
    }
    expected_output_token = {
        "limit": "1",
        "page_info": "eyJjcmVhdGVkX2",
    }

    requests_mock.get("https://test.myshopify.com/", headers=response_header_links)
    response = requests.get("https://test.myshopify.com/")

    test = ShopifyStream.next_page_token(response)
    assert test == expected_output_token
