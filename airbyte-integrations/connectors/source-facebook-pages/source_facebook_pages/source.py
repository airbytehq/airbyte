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


from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Page, PageInsights, Post, PostInsights


class SourceFacebookPages(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        params = {
            "access_token": config["access_token"],
        }

        response = requests.get("https://graph.facebook.com/v11.0/me", params=params)
        if response.status_code == 200:
            return True, None
        else:
            return False, f"Unable to connect to Facebook API with the provided credentials {response.content}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_kwargs = {
            "access_token": config["access_token"],
            "page_id": config["page_id"],
        }
        incremental_stream_kwargs = {**stream_kwargs}
        if config.get("start_date"):
            incremental_stream_kwargs["start_date"] = pendulum.parse(config["start_date"])
        streams = [
            Post(**incremental_stream_kwargs),
            Page(**incremental_stream_kwargs),
            PostInsights(**incremental_stream_kwargs),
            PageInsights(**incremental_stream_kwargs),
        ]
        return streams
