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

from requests.sessions import session
import requests_mock
import requests
from source_shopify.source import ShopifyStream
from airbyte_cdk.sources.streams.http import HttpStream
import source_shopify.source

response_header_links = {
    "Date": "Thu, 24 Jun 2021 14:49:20 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Transfer-Encoding": "chunked",
    "Link": '<https://jolicookie.myshopify.com/admin/api/2021-04/customers.json?limit=1&page_info=eyJjcmVhdGVkX2F0X21pbiI6IjIwMjAtMDQtMDEgMDA6MDA6MDAgVVRDIiwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjozNjA0NjIxMTMxOTM0LCJsYXN0X3ZhbHVlIjozNjA0NjIxMTMxOTM0LCJkaXJlY3Rpb24iOiJuZXh0In0>; rel="next"'
}
expected_output = {'page_info': 'eyJjcmVhdGVkX2F0X21pbiI6IjIwMjAtMDQtMDEgMDA6MDA6MDAgVVRDIiwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjozNjA0NjIxMTMxOTM0LCJsYXN0X3ZhbHVlIjozNjA0NjIxMTMxOTM0LCJkaXJlY3Rpb24iOiJuZXh0In0'}


class TestNextPageLink():

    """
    The test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call, 
    """

    def test_get_next_page_token(self, requests_mock):
        requests_mock.get("https://jolicookie.myshopify.com/", text="data", headers=response_header_links)
        response = requests.get("https://jolicookie.myshopify.com/")

        test = ShopifyStream.next_page_token(self, response = response)
        self.response = response
        assert test == expected_output

        return self.response


    def test_real_call(self):
        response = self.response
        next_page_url = response.links.get("next", None).get("url")

        session = requests.get(next_page_url)
        data = session.json()

        print(data)

    


    

        


