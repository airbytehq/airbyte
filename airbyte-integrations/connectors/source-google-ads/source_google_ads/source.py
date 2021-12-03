#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException
from pendulum import timezone
from pendulum.tz.timezone import Timezone

from .custom_query_stream import CustomQuery
from .google_ads import GoogleAds
from .streams import (
    AccountPerformanceReport,
    Accounts,
    AdGroupAdReport,
    AdGroupAds,
    AdGroups,
    Campaigns,
    ClickView,
    DisplayKeywordPerformanceReport,
    DisplayTopicsPerformanceReport,
    ShoppingPerformanceReport,
    UserLocationReport,
)


class SourceGoogleAds(AbstractSource):
    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config["credentials"]

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    @staticmethod
    def get_time_zone(google_api) -> [timezone, str]:
        account = next(Accounts(api=google_api).read_records(sync_mode=None), {})
        time_zone_name = account.get("customer.time_zone")
        if time_zone_name:
            return Timezone(time_zone_name)
        return "local"

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
        time_zone = self.get_time_zone(google_api)
        incremental_stream_config = dict(
            api=google_api,
            conversion_window_days=config["conversion_window_days"],
            start_date=config["start_date"],
            time_zone=time_zone
        )

        streams = [
            AdGroupAds(api=google_api),
            AdGroups(api=google_api),
            Accounts(api=google_api),
            Campaigns(api=google_api),
            ClickView(**incremental_stream_config),
        ]

        custom_query_streams = [
            CustomQuery(custom_query_config=single_query_config, **incremental_stream_config)
            for single_query_config in config.get("custom_queries", [])
        ]
        streams.extend(custom_query_streams)

        is_manager_account = "login_customer_id" in config and config["login_customer_id"].strip()
        # Metrics streams cannot be requested for a manager account.
        if not is_manager_account:
            streams.extend([
                UserLocationReport(**incremental_stream_config),
                AccountPerformanceReport(**incremental_stream_config),
                DisplayTopicsPerformanceReport(**incremental_stream_config),
                DisplayKeywordPerformanceReport(**incremental_stream_config),
                ShoppingPerformanceReport(**incremental_stream_config),
                AdGroupAdReport(**incremental_stream_config)
            ])
        return streams
