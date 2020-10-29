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

import json
import pkgutil
import urllib.request

from airbyte_protocol import AirbyteCatalog, ConnectorSpecification
from base_python_test import StandardSourceTestIface


class GoogleAnalyticsStandardSourceTest(StandardSourceTestIface):
    def get_spec(self) -> ConnectorSpecification:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    def get_config(self) -> object:
        return json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], "config.json"))

    def get_catalog(self) -> AirbyteCatalog:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], "test_catalog.json")
        return AirbyteCatalog.parse_obj(json.loads(raw_spec))

    # send a pageview to GA
    def setup(self) -> None:
        tracker = pkgutil.get_data(self.__class__.__module__.split(".")[0], "tracker.txt").strip()
        pageview_url = f"https://www.google-analytics.com/j/collect?v=1&_v=j86&a=1532168960&t=pageview&_s=1&dl=https%3A%2F%2Fairbyte.io&de=UTF-8&dt=Page%20Title&sd=30-bit&sr=1440x900&vp=344x650&je=0&_u=AACAAUABAAAAAC~&jid=1183258623&gjid=1930938845&cid=1690909460.1603818157&tid={tracker}"
        urllib.request.urlopen(pageview_url)

    def teardown(self) -> None:
        pass

    # todo: add regexes that must match and regexes that must not match
