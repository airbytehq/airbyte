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
from urllib.parse import quote_plus

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_google_search_console.streams import (
    SearchAnalyticsAllFields,
    SearchAnalyticsByCountry,
    SearchAnalyticsByDate,
    SearchAnalyticsByDevice,
    SearchAnalyticsByPage,
    SearchAnalyticsByQuery,
    Sitemaps,
    Sites,
)


class SourceGoogleSearchConsole(AbstractSource):
    def check_connection(
        self, logger: AirbyteLogger, config: Mapping[str, Any]
    ) -> Tuple[bool, Any]:
        try:
            stream_kwargs = self.get_stream_kwargs(config)
            sites = Sites(**stream_kwargs)
            sites_gen = sites.read_records(sync_mode=SyncMode.full_refresh)
            next(sites_gen)
            return True, None

        except Exception as error:
            return (
                False,
                f"Unable to connect to Google Search Console API with the provided credentials - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_kwargs = self.get_stream_kwargs(config)
        streams = [
            Sites(**stream_kwargs),
            Sitemaps(**stream_kwargs),
            SearchAnalyticsByCountry(**stream_kwargs),
            SearchAnalyticsByDevice(**stream_kwargs),
            SearchAnalyticsByDate(**stream_kwargs),
            SearchAnalyticsByQuery(**stream_kwargs),
            SearchAnalyticsByPage(**stream_kwargs),
            SearchAnalyticsAllFields(**stream_kwargs),
        ]

        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]):
        stream_kwargs = {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "refresh_token": config.get("refresh_token"),
            "site_url": quote_plus(config.get("site_url")),
            "start_date": config.get("start_date"),
        }

        return stream_kwargs
