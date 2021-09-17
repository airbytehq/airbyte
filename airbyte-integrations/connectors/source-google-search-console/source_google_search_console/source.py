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
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stream_kwargs = self.get_stream_kwargs(config)
            sites = Sites(**stream_kwargs)
            stream_slice = next(sites.stream_slices(SyncMode.full_refresh))
            sites_gen = sites.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
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

        stream_config = self.get_stream_kwargs(config)

        streams = [
            Sites(**stream_config),
            Sitemaps(**stream_config),
            SearchAnalyticsByCountry(**stream_config),
            SearchAnalyticsByDevice(**stream_config),
            SearchAnalyticsByDate(**stream_config),
            SearchAnalyticsByQuery(**stream_config),
            SearchAnalyticsByPage(**stream_config),
            SearchAnalyticsAllFields(**stream_config),
        ]

        return streams

    @staticmethod
    def get_stream_kwargs(config: Mapping[str, Any]):
        authorization = config.get("authorization", {})

        stream_kwargs = {
            "auth_type": config.get("authorization", {}).get("auth_type"),
            "site_urls": config.get("site_urls"),
            "start_date": config.get("start_date"),
            "end_date": config.get("end_date"),
        }

        if stream_kwargs["auth_type"] == "Client":
            stream_kwargs["client_id"] = authorization.get("client_id")
            stream_kwargs["client_secret"] = authorization.get("client_secret")
            stream_kwargs["refresh_token"] = authorization.get("refresh_token")
        else:
            stream_kwargs["service_account_info"] = authorization.get("service_account_info")

        return stream_kwargs
