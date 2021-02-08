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

import pkgutil
from typing import List

import requests
from base_python_test import DefaultStandardSourceTest


class GoogleAnalyticsStandardSourceTest(DefaultStandardSourceTest):
    CONFIGURED_CATALOG_FILENAME = "test_catalog.json"

    # send a page view to GA using a URL constructed with
    # the documentation from https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide#page
    # and the hit builder at https://ga-dev-tools.appspot.com/hit-builder/
    # and converted into Python
    def setup(self) -> None:
        tracker = pkgutil.get_data(self.__class__.__module__.split(".")[0], "tracker.txt").strip()
        url = "https://www.google-analytics.com/collect"
        payload = {"v": "1", "t": "pageview", "tid": tracker, "cid": "555", "dh": "mydemo.com", "dp": "/home5", "dt": "homepage"}
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://ga-dev-tools.appspot.com",
            "referer": "https://ga-dev-tools.appspot.com/",
        }
        requests.post(url, data=payload, headers=headers)

    def get_regex_tests(self) -> List[str]:
        return [
            "(.*)RECORD(.*)website_overview(.*)",
            "(.*)RECORD(.*)traffic_sources(.*)",
            "(.*)RECORD(.*)pages(.*)",
            "(.*)RECORD(.*)locations(.*)",
            "(.*)RECORD(.*)monthly_active_users(.*)",
            "(.*)RECORD(.*)four_weekly_active_users(.*)",
            "(.*)RECORD(.*)two_weekly_active_users(.*)",
            "(.*)RECORD(.*)weekly_active_users(.*)",
            "(.*)RECORD(.*)daily_active_users(.*)",
            "(.*)RECORD(.*)devices(.*)",
        ]

    # todo: add regexes that must match and regexes that must not match
