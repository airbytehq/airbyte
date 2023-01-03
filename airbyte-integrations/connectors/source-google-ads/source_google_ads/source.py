#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import traceback
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException
from pendulum import parse, today

from .custom_query_stream import CustomQuery
from .google_ads import GoogleAds
from .models import Customer
from .streams import (
    AccountPerformanceReport,
    Accounts,
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
    ServiceAccounts,
    ShoppingPerformanceReport,
    UserLocationReport,
)


class SourceGoogleAds(AbstractSource):
    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any]):
        if config.get("end_date") == "":
            config.pop("end_date")
        return config

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
        end_date = config.get("end_date")
        if end_date:
            end_date = min(today(), parse(end_date)).to_date_string()
        incremental_stream_config = dict(
            api=google_api,
            customers=customers,
            conversion_window_days=config["conversion_window_days"],
            start_date=config["start_date"],
            end_date=end_date,
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

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        config = self._validate_and_transform(config)
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
                        logger.warning(
                            f"Metrics are not available for manager account {customer.id}. "
                            f"Please remove metrics fields in your custom query: {query}."
                        )
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
            return False, f"Unable to connect to Google Ads API with the provided configuration - {error_messages}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        google_api = GoogleAds(credentials=self.get_credentials(config))
        accounts = self.get_account_info(google_api, config)
        customers = Customer.from_accounts(accounts)
        non_manager_accounts = [customer for customer in customers if not customer.is_manager_account]
        incremental_config = self.get_incremental_stream_config(google_api, config, customers)
        non_manager_incremental_config = self.get_incremental_stream_config(google_api, config, non_manager_accounts)
        streams = [
            AdGroupAds(**incremental_config),
            AdGroupAdLabels(google_api, customers=customers),
            AdGroups(**incremental_config),
            AdGroupLabels(google_api, customers=customers),
            Accounts(**incremental_config),
            CampaignLabels(google_api, customers=customers),
            ClickView(**incremental_config),
        ]
        # Metrics streams cannot be requested for a manager account.
        if non_manager_accounts:
            streams.extend(
                [
                    Campaigns(**non_manager_incremental_config),
                    UserLocationReport(**non_manager_incremental_config),
                    AccountPerformanceReport(**non_manager_incremental_config),
                    DisplayTopicsPerformanceReport(**non_manager_incremental_config),
                    DisplayKeywordPerformanceReport(**non_manager_incremental_config),
                    ShoppingPerformanceReport(**non_manager_incremental_config),
                    AdGroupAdReport(**non_manager_incremental_config),
                    GeographicReport(**non_manager_incremental_config),
                    KeywordReport(**non_manager_incremental_config),
                ]
            )
        for single_query_config in config.get("custom_queries", []):
            query = single_query_config.get("query")
            if self.is_metrics_in_custom_query(query):
                if non_manager_accounts:
                    streams.append(CustomQuery(custom_query_config=single_query_config, **non_manager_incremental_config))
                continue
            streams.append(CustomQuery(custom_query_config=single_query_config, **incremental_config))
        return streams
