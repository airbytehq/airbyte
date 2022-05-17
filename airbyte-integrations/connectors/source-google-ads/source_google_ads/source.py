#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import traceback
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException
from pendulum import parse, timezone, today

from .custom_query_stream import CustomQuery
from .google_ads import GoogleAds
from .models import Customer
from .streams import (
    AccountPerformanceReport,
    Accounts,
    ServiceAccounts,
    AdGroupAdLabels,
    AdGroupAdReport,
    AdGroupAds,
    AdGroupLabels,
    AdGroups,
    CampaignLabels,
    Campaigns,
    ClickView,
    DisplayKeywordPerformanceReport,
    DisplayTopicsPerformanceReport,
    GeographicReport,
    KeywordReport,
    ShoppingPerformanceReport,
    UserLocationReport,
)


class SourceGoogleAds(AbstractSource):
    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
        credentials = config["credentials"]
        # use_proto_plus is set to True, because setting to False returned wrong value types, which breakes the backward compatibility.
        # For more info read the related PR's description: https://github.com/airbytehq/airbyte/pull/9996
        credentials.update(use_proto_plus=True)

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    @staticmethod
    def get_incremental_stream_config(google_api: GoogleAds, config: Mapping[str, Any], customers: List[Customer]):
        true_end_date = None
        configured_end_date = config.get("end_date")
        if configured_end_date is not None:
            true_end_date = min(today(), parse(configured_end_date)).to_date_string()
        incremental_stream_config = dict(
            api=google_api,
            customers=customers,
            conversion_window_days=config["conversion_window_days"],
            start_date=config["start_date"],
            end_date=true_end_date,
        )
        return incremental_stream_config

    def get_account_info(self, google_api: GoogleAds, config: Mapping[str, Any]) -> Iterable[Iterable[Mapping[str, Any]]]:
        dummy_customers = [Customer(id=_id) for _id in config["customer_id"].split(",")]
        accounts_stream = ServiceAccounts(google_api, customers=dummy_customers)
        for slice_ in accounts_stream.stream_slices():
            yield accounts_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_)

    @staticmethod
    def is_metrics_in_custom_query(query: str) -> bool:
        fields = CustomQuery.get_query_fields(query)
        for field in fields:
            if field.startswith("metrics"):
                return True
        return False

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            logger.info("Checking the config")
            google_api = GoogleAds(credentials=self.get_credentials(config))

            accounts = self.get_account_info(google_api, config)
            customers = Customer.from_accounts(accounts)
            # Check custom query request validity by sending metric request with non-existant time window
            for customer in customers:
                for query in config.get("custom_queries", []):
                    query = query.get("query")
                    if customer.is_manager_account and self.is_metrics_in_custom_query(query):
                        return False, f"Metrics are not available for manager account. Check fields in your custom query: {query}"
                    if CustomQuery.cursor_field in query:
                        return False, f"Custom query should not contain {CustomQuery.cursor_field}"
                    req_q = CustomQuery.insert_segments_date_expr(query, "1980-01-01", "1980-01-01")
                    response = google_api.send_request(req_q, customer_id=customer.id)
                    # iterate over the response otherwise exceptions will not be raised!
                    for _ in response:
                        pass
            return True, None
        except GoogleAdsException as exception:
            error_messages = ", ".join([error.message for error in exception.failure.errors])
            logger.error(traceback.format_exc())
            return False, f"Unable to connect to Google Ads API with the provided credentials - {error_messages}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        google_api = GoogleAds(credentials=self.get_credentials(config))
        accounts = self.get_account_info(google_api, config)
        customers = Customer.from_accounts(accounts)
        incremental_stream_config = self.get_incremental_stream_config(google_api, config, customers)
        streams = [
            AdGroupAds(**incremental_stream_config),
            AdGroupAdLabels(google_api, customers=customers),
            AdGroups(**incremental_stream_config),
            AdGroupLabels(google_api, customers=customers),
            Accounts(**incremental_stream_config),
            Campaigns(**incremental_stream_config),
            CampaignLabels(google_api, customers=customers),
            ClickView(**incremental_stream_config),
        ]
        custom_query_streams = [
            CustomQuery(custom_query_config=single_query_config, **incremental_stream_config)
            for single_query_config in config.get("custom_queries", [])
        ]
        streams.extend(custom_query_streams)

        # Metrics streams cannot be requested for a manager account.
        non_manager_accounts = [customer for customer in customers if not customer.is_manager_account]
        if non_manager_accounts:
            incremental_stream_config["customers"] = non_manager_accounts
            streams.extend(
                [
                    UserLocationReport(**incremental_stream_config),
                    AccountPerformanceReport(**incremental_stream_config),
                    DisplayTopicsPerformanceReport(**incremental_stream_config),
                    DisplayKeywordPerformanceReport(**incremental_stream_config),
                    ShoppingPerformanceReport(**incremental_stream_config),
                    AdGroupAdReport(**incremental_stream_config),
                    GeographicReport(**incremental_stream_config),
                    KeywordReport(**incremental_stream_config),
                ]
            )
        return streams
