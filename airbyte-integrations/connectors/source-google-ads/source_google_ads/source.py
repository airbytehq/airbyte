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

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException

from .custom_query_stream import CustomQuery
from .google_ads import GoogleAds
from .streams import (
    AccountPerformanceReport,
    Accounts,
    AdGroupAdReport,
    AdGroupAds,
    AdGroups,
    Campaigns,
    DisplayKeywordPerformanceReport,
    DisplayTopicsPerformanceReport,
    ShoppingPerformanceReport,
    UserLocationReport,
)


class SourceGoogleAds(AbstractSource):
    def get_credentials(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config["credentials"]

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            logger.info("Checking the config")
            google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
            account_stream = Accounts(api=google_api)
            list(account_stream.read_records(sync_mode=SyncMode.full_refresh))
            # Check custom query request validity by sending metric request with non-existant time window
            for q in config.get("custom_queries", []):
                q = q.get("query")
                if CustomQuery.cursor_field in q:
                    raise Exception(f"Custom query should not contain {CustomQuery.cursor_field}")
                req_q = CustomQuery.insert_segments_date_expr(q, "1980-01-01", "1980-01-01")
                google_api.send_request(req_q)
            return True, None
        except GoogleAdsException as error:
            return False, f"Unable to connect to Google Ads API with the provided credentials - {repr(error.failure)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
        incremental_stream_config = dict(
            api=google_api, conversion_window_days=config["conversion_window_days"], start_date=config["start_date"]
        )

        custom_query_streams = [
            CustomQuery(custom_query_config=single_query_config, **incremental_stream_config)
            for single_query_config in config.get("custom_queries", [])
        ]
        return [
            UserLocationReport(**incremental_stream_config),
            AccountPerformanceReport(**incremental_stream_config),
            DisplayTopicsPerformanceReport(**incremental_stream_config),
            DisplayKeywordPerformanceReport(**incremental_stream_config),
            ShoppingPerformanceReport(**incremental_stream_config),
            AdGroupAdReport(**incremental_stream_config),
            AdGroupAds(api=google_api),
            AdGroups(api=google_api),
            Accounts(api=google_api),
            Campaigns(api=google_api),
        ] + custom_query_streams
