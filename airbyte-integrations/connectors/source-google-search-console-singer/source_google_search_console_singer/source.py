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

from base_python import AirbyteLogger
from base_singer import BaseSingerSource
from tap_google_search_console.client import GoogleClient


class SourceGoogleSearchConsoleSinger(BaseSingerSource):
    tap_cmd = "tap-google-search-console"
    tap_name = "Google Search Console API"
    api_error = Exception

    def try_connect(self, logger: AirbyteLogger, config: json):
        google_client = GoogleClient(credentials_json=config.get("credentials_json"), email=config.get("email"))
        site_urls = config.get("site_urls").replace(" ", "").split(",")
        for site in site_urls:
            google_client.get(method_name="get", resource_name="sites", params={"siteUrl": site})
