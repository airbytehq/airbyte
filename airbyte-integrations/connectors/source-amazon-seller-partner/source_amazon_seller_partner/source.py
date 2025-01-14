#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from logging import Logger
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from requests import HTTPError

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException, is_cloud_environment
from airbyte_protocol.models import ConnectorSpecification
from source_amazon_seller_partner.auth import AWSAuthenticator
from source_amazon_seller_partner.constants import get_marketplaces
from source_amazon_seller_partner.streams import (
    BrandAnalyticsMarketBasketReports,
    BrandAnalyticsRepeatPurchaseReports,
    BrandAnalyticsSearchTermsReports,
    FbaAfnInventoryByCountryReports,
    FbaAfnInventoryReports,
    FbaCustomerReturnsReports,
    FbaEstimatedFbaFeesTxtReport,
    FbaFulfillmentCustomerShipmentPromotionReport,
    FbaInventoryPlaningReport,
    FbaMyiUnsuppressedInventoryReport,
    FbaOrdersReports,
    FbaReimbursementsReports,
    FbaReplacementsReports,
    FbaShipmentsReports,
    FbaSnsForecastReport,
    FbaSnsPerformanceReport,
    FbaStorageFeesReports,
    FlatFileActionableOrderDataShipping,
    FlatFileArchivedOrdersDataByOrderDate,
    FlatFileOpenListingsReports,
    FlatFileOrdersReports,
    FlatFileOrdersReportsByLastUpdate,
    FlatFileReturnsDataByReturnDate,
    FlatFileSettlementV2Reports,
    FulfilledShipmentsReports,
    GetXmlBrowseTreeData,
    LedgerDetailedViewReports,
    LedgerSummaryViewReport,
    ListFinancialEventGroups,
    ListFinancialEvents,
    MerchantCancelledListingsReport,
    MerchantListingsFypReport,
    MerchantListingsInactiveData,
    MerchantListingsReport,
    MerchantListingsReportBackCompat,
    MerchantListingsReports,
    NetPureProductMarginReport,
    OrderItems,
    OrderReportDataShipping,
    Orders,
    RapidRetailAnalyticsInventoryReport,
    ReportsAmazonSPStream,
    RestockInventoryReports,
    SellerAnalyticsSalesAndTrafficReports,
    SellerFeedbackReports,
    StrandedInventoryUiReport,
    VendorDirectFulfillmentShipping,
    VendorForecastingFreshReport,
    VendorForecastingRetailReport,
    VendorInventoryReports,
    VendorOrders,
    VendorSalesReports,
    VendorTrafficReport,
    XmlAllOrdersDataByOrderDataGeneral,
)
from source_amazon_seller_partner.utils import AmazonConfigException


# given the retention period: 730
DEFAULT_RETENTION_PERIOD_IN_DAYS = 730


class SourceAmazonSellerPartner(AbstractSource):
    @staticmethod
    def _get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        endpoint, marketplace_id, _ = get_marketplaces(config.get("aws_environment"))[config.get("region")]
        auth = AWSAuthenticator(
            token_refresh_endpoint="https://api.amazon.com/auth/o2/token",
            client_id=config.get("lwa_app_id"),
            client_secret=config.get("lwa_client_secret"),
            refresh_token=config.get("refresh_token"),
            host=endpoint.replace("https://", ""),
            refresh_access_token_headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        start_date = config.get("replication_start_date")
        use_default_start_date = (
            not start_date or (pendulum.now("utc") - pendulum.parse(start_date)).days > DEFAULT_RETENTION_PERIOD_IN_DAYS
        )
        if use_default_start_date:
            start_date = pendulum.now("utc").subtract(days=DEFAULT_RETENTION_PERIOD_IN_DAYS).strftime("%Y-%m-%dT%H:%M:%SZ")

        end_date = config.get("replication_end_date")
        use_default_end_date = not end_date or end_date < start_date
        if use_default_end_date:
            end_date = None  # None to sync all data

        stream_kwargs = {
            "url_base": endpoint,
            "authenticator": auth,
            "replication_start_date": start_date,
            "marketplace_id": marketplace_id,
            "period_in_days": config.get("period_in_days", 365),
            "replication_end_date": end_date,
        }
        return stream_kwargs

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Check connection to Amazon SP API by requesting the Orders endpoint
        This endpoint is not available for vendor-only Seller accounts,
        the Orders endpoint will then return a 403 error
        Therefore made an exception for 403 errors (when vendor-only accounts).
        When no access, a 401 error is given.
        Validate if response has the expected error code and body.
        Show error message in case of request exception or unexpected response.
        """
        try:
            self.validate_replication_dates(config)
            self.validate_stream_report_options(config)
            stream_kwargs = self._get_stream_kwargs(config)

            if config.get("account_type", "Seller") == "Seller":
                stream_to_check = Orders(**stream_kwargs)
                next(stream_to_check.read_records(sync_mode=SyncMode.full_refresh))
            else:
                stream_to_check = VendorOrders(**stream_kwargs)
                stream_slices = list(stream_to_check.stream_slices(sync_mode=SyncMode.full_refresh))
                next(stream_to_check.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices[0]))

            return True, None
        except Exception as e:
            # Validate stream without data
            if isinstance(e, StopIteration):
                return True, None

            if isinstance(e, HTTPError):
                return False, e.response.json().get("error_description")
            else:
                error_message = "Caught unexpected exception during the check"
                raise AirbyteTracedException(internal_message=error_message, message=error_message, exception=e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        self.validate_stream_report_options(config)
        streams = []
        stream_kwargs = self._get_stream_kwargs(config)
        stream_list = [
            FbaCustomerReturnsReports,
            FbaAfnInventoryReports,
            FbaAfnInventoryByCountryReports,
            FbaOrdersReports,
            FbaShipmentsReports,
            FbaReplacementsReports,
            FbaStorageFeesReports,
            RestockInventoryReports,
            FlatFileActionableOrderDataShipping,
            FlatFileOpenListingsReports,
            FlatFileOrdersReports,
            FlatFileOrdersReportsByLastUpdate,
            FlatFileSettlementV2Reports,
            FulfilledShipmentsReports,
            MerchantListingsReports,
            VendorDirectFulfillmentShipping,
            Orders,
            OrderItems,
            OrderReportDataShipping,
            SellerFeedbackReports,
            GetXmlBrowseTreeData,
            ListFinancialEventGroups,
            ListFinancialEvents,
            LedgerDetailedViewReports,
            FbaEstimatedFbaFeesTxtReport,
            FbaFulfillmentCustomerShipmentPromotionReport,
            FbaMyiUnsuppressedInventoryReport,
            MerchantCancelledListingsReport,
            MerchantListingsReport,
            MerchantListingsReportBackCompat,
            MerchantListingsInactiveData,
            StrandedInventoryUiReport,
            XmlAllOrdersDataByOrderDataGeneral,
            MerchantListingsFypReport,
            FbaSnsForecastReport,
            FbaSnsPerformanceReport,
            FlatFileArchivedOrdersDataByOrderDate,
            FlatFileReturnsDataByReturnDate,
            FbaInventoryPlaningReport,
            LedgerSummaryViewReport,
            FbaReimbursementsReports,
            VendorOrders,
            VendorForecastingFreshReport,
            VendorForecastingRetailReport,
        ]

        # TODO: Remove after Brand Analytics will be enabled in CLOUD: https://github.com/airbytehq/airbyte/issues/32353
        if not is_cloud_environment():
            brand_analytics_reports = [
                BrandAnalyticsMarketBasketReports,
                BrandAnalyticsSearchTermsReports,
                BrandAnalyticsRepeatPurchaseReports,
                SellerAnalyticsSalesAndTrafficReports,
                VendorSalesReports,
                VendorInventoryReports,
                NetPureProductMarginReport,
                RapidRetailAnalyticsInventoryReport,
                VendorTrafficReport,
            ]
            stream_list += brand_analytics_reports

        for stream in stream_list:
            if not issubclass(stream, ReportsAmazonSPStream):
                streams.append(stream(**stream_kwargs))
                continue
            report_kwargs = list(self.get_stream_report_kwargs(stream.report_name, config))
            if not report_kwargs:
                report_kwargs.append((stream.report_name, {}))
            for name, options in report_kwargs:
                kwargs = {
                    "stream_name": name,
                    "report_options": options,
                    "wait_to_avoid_fatal_errors": config.get("wait_to_avoid_fatal_errors", False),
                    **stream_kwargs,
                }
                streams.append(stream(**kwargs))
        return streams

    def spec(self, logger: Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        if not is_cloud_environment():
            oss_only_streams = [
                "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
                "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
                "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
                "GET_VENDOR_SALES_REPORT",
                "GET_VENDOR_INVENTORY_REPORT",
                "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT",
                "GET_VENDOR_TRAFFIC_REPORT",
            ]
            spec.connectionSpecification["properties"]["report_options_list"]["items"]["properties"]["report_name"]["enum"].extend(
                oss_only_streams
            )

        return spec

    @staticmethod
    def validate_replication_dates(config: Mapping[str, Any]) -> None:
        if (
            "replication_start_date" in config
            and "replication_end_date" in config
            and config["replication_end_date"] < config["replication_start_date"]
        ):
            raise AmazonConfigException(message="End Date should be greater than or equal to Start Date")

    @staticmethod
    def validate_stream_report_options(config: Mapping[str, Any]) -> None:
        options_list = config.get("report_options_list", [])
        stream_names = [x.get("stream_name") for x in options_list]
        if len(stream_names) != len(set(stream_names)):
            raise AmazonConfigException(message="Stream name should be unique among all Report options list")

        for report_option in options_list:
            option_names = [x.get("option_name") for x in report_option.get("options_list")]
            if len(option_names) != len(set(option_names)):
                raise AmazonConfigException(
                    message=f"Option names should be unique for `{report_option.get('stream_name')}` report options"
                )

    @staticmethod
    def get_stream_report_kwargs(report_name: str, config: Mapping[str, Any]) -> List[Tuple[str, Optional[List[Mapping[str, Any]]]]]:
        options_list = config.get("report_options_list", [])
        for x in options_list:
            if x.get("report_name") == report_name:
                yield x.get("stream_name"), x.get("options_list")
