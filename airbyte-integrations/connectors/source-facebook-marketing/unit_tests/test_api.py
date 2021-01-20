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

from unittest.mock import Mock
from source_facebook_marketing.client.api import AdCreativeAPI


class TestAdCreativeAPI:
    def test_init(self):
        api_mock = Mock()

        api = AdCreativeAPI(api=api_mock)
        api.list(fields=[])


class TestCampaignAPI:
    def test__init(self):
        api_mock = Mock()
        api_mock.account.get_ad_creatives.return_value = [1, 2, 3]

        api = AdCreativeAPI(api=api_mock)


    def test__list(self):
        api.list(fields=[])

    def test__list_with_state(self):
        api.list()


class TestAdSetsAPI:
    pass


class TestAdsAPI:
    pass
