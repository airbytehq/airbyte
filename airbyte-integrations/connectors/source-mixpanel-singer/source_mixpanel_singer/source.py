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

from datetime import datetime, timedelta

from base_python import AirbyteLogger
from base_singer import BaseSingerSource
from tap_mixpanel.client import MixpanelClient, MixpanelError


class SourceMixpanelSinger(BaseSingerSource):
    tap_cmd = "tap-mixpanel"
    tap_name = "Mixpanel API"
    api_error = MixpanelError
    client_class = MixpanelClient

    USER_AGENT = "tap-mixpanel contact@airbyte.io"

    @property
    def default_start_date(self):
        one_year_ago = datetime.now() - timedelta(days=365)
        return one_year_ago.replace(microsecond=0).isoformat() + "Z"

    def transform_config(self, raw_config):
        airbyte_config = {
            "user_agent": self.USER_AGENT,
            "api_secret": raw_config["api_secret"],
            "start_date": raw_config.get("start_date", self.default_start_date),
            "date_window_size": raw_config.get("date_window_size", 30),
            "attribution_window": raw_config.get("attribution_window", 5),
            "project_timezone": raw_config.get("project_timezone", "US/Pacific"),
            "select_properties_by_default": raw_config.get("select_properties_by_default", True),
        }
        # drop None values as some of them has no default fallback
        return {k: v for k, v in airbyte_config.items() if v is not None}

    def try_connect(self, logger: AirbyteLogger, config: dict):
        client = self.client_class(user_agent=config["user_agent"], api_secret=config["api_secret"])
        ok = client.check_access()
        if not ok:
            raise self.api_error("No data. Please check your permissions.")
