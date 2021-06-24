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

import requests_mock
import requests
from source_shopify.source import ShopifyStream, ShopifyAuthenticator

response_header_links = {
    "Date": "Thu, 32 Jun 2099 24:24:24 GMT",
    "Content-Type": "application/json; charset=utf-8",
    "Link": '<https://test_shop.myshopify.com/admin/api/2021-04/test_object.json?limit=1&page_info=eyJjcmVhdGVkX2F0X21pbiI6IjIwMjAtMDQtMDEgMDA6MDA6MDAgVVRDIiwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjozNjA0NjIxMTMxOTM0LCJsYXN0X3ZhbHVlIjozNjA0NjIxMTMxOTM0LCJkaXJlY3Rpb24iOiJuZXh0In0>; rel="next"'
}

expected_output_token = {'page_info': 'eyJjcmVhdGVkX2F0X21pbiI6IjIwMjAtMDQtMDEgMDA6MDA6MDAgVVRDIiwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjozNjA0NjIxMTMxOTM0LCJsYXN0X3ZhbHVlIjozNjA0NjIxMTMxOTM0LCJkaXJlY3Rpb24iOiJuZXh0In0'}
start_page_link = 'https://jolicookie.myshopify.com/admin/api/2021-04/customers.json?limit=1&page_info=eyJjcmVhdGVkX2F0X21pbiI6IjIwMjAtMDQtMDEgMDA6MDA6MDAgVVRDIiwib3JkZXIiOiJpZCBhc2MiLCJsYXN0X2lkIjozNjA0NjIxMTMxOTM0LCJsYXN0X3ZhbHVlIjozNjA0NjIxMTMxOTM0LCJkaXJlY3Rpb24iOiJuZXh0In0'

class TestNextPageToken:

    def test_get_next_page_token(self, requests_mock):
        """
        Test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call, 
        """

        requests_mock.get("https://test.myshopify.com/", headers=response_header_links)
        response = requests.get("https://test.myshopify.com/")

        test = ShopifyStream.next_page_token(self, response=response)
        assert test == expected_output_token


class TestNextPageCall:

    token = "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"

    def test_next_page_call(self):
        """
        Test produces 1 real call to API destination to check the pagination works.
        """

        auth_header = ShopifyAuthenticator(token=self.token).get_auth_header()
        session = requests.get(start_page_link, headers=auth_header)
        data = session.json()
        previous_page = session.links.get("previous", None).get("url")
        next_page = session.links.get("next", None).get("url")

        # if ok, we would have previous_page, next_page, and the data as the response from the previous page
        if previous_page and data and next_page:
            assert True
        else:
            assert False






    

    


    

        


