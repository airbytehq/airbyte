#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import traceback
from typing import Any, Iterable, List, Mapping, MutableMapping, Tuple

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v13.errors.types.authentication_error import AuthenticationErrorEnum
from google.ads.googleads.v13.errors.types.authorization_error import AuthorizationErrorEnum
from pendulum import parse, today

from .custom_query_stream import CustomQuery, IncrementalCustomQuery
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
from .utils import GAQL

FULL_REFRESH_CUSTOM_TABLE = ["asset", "asset_group_listing_group_filter", "custom_audience", "geo_target_constant"]


class SourceGoogleAds(AbstractSource):
    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any]):
        if config.get("end_date") == "":
            config.pop("end_date")
        for query in config.get("custom_queries", []):
            try:
                query["query"] = GAQL.parse(query["query"])
            except ValueError:
                message = f"The custom GAQL query {query['table_name']} failed. Validate your GAQL query with the Google Ads query validator. https://developers.google.com/google-ads/api/fields/v13/query_validator"
                raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)
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
    def is_metrics_in_custom_query(query: GAQL) -> bool:
        for field in query.fields:
            if field.split(".")[0] == "metrics":
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
                    query = query["query"]
                    if customer.is_manager_account and self.is_metrics_in_custom_query(query):
                        logger.warning(
                            f"Metrics are not available for manager account {customer.id}. "
                            f"Please remove metrics fields in your custom query: {query}."
                        )
                    if query.resource_name not in FULL_REFRESH_CUSTOM_TABLE:
                        if IncrementalCustomQuery.cursor_field in query.fields:
                            return False, f"Custom query should not contain {IncrementalCustomQuery.cursor_field}"
                        query = IncrementalCustomQuery.insert_segments_date_expr(query, "1980-01-01", "1980-01-01")
                    query = query.set_limit(1)
                    response = google_api.send_request(str(query), customer_id=customer.id)
                    # iterate over the response otherwise exceptions will not be raised!
                    for _ in response:
                        pass
            return True, None
        except GoogleAdsException as exception:
            if AuthorizationErrorEnum.AuthorizationError.USER_PERMISSION_DENIED in (
                x.error_code.authorization_error for x in exception.failure.errors
            ) or AuthenticationErrorEnum.AuthenticationError.CUSTOMER_NOT_FOUND in (
                x.error_code.authentication_error for x in exception.failure.errors
            ):
                message = f"Failed to access the customer '{exception.customer_id}'. Ensure the customer is linked to your manager account or check your permissions to access this customer account."
                raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)
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
            query = single_query_config["query"]
            if self.is_metrics_in_custom_query(query):
                if non_manager_accounts:
                    if query.resource_name in FULL_REFRESH_CUSTOM_TABLE:
                        streams.append(CustomQuery(config=single_query_config, api=google_api, customers=non_manager_accounts))
                    else:
                        streams.append(IncrementalCustomQuery(config=single_query_config, **non_manager_incremental_config))
                continue
            if query.resource_name in FULL_REFRESH_CUSTOM_TABLE:
                streams.append(CustomQuery(config=single_query_config, api=google_api, customers=customers))
            else:
                streams.append(IncrementalCustomQuery(config=single_query_config, **incremental_config))
        return streams
