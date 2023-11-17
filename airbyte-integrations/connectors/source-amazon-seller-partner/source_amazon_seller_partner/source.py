#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from os import getenv
from typing import Any, List, Mapping, Tuple, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner.auth import AWSAuthenticator
from source_amazon_seller_partner.constants import get_marketplaces
from source_amazon_seller_partner.streams import (
    BrandAnalyticsAlternatePurchaseReports,
    BrandAnalyticsItemComparisonReports,
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
    OrderItems,
    OrderReportDataShipping,
    Orders,
    RestockInventoryReports,
    SellerAnalyticsSalesAndTrafficReports,
    SellerFeedbackReports,
    StrandedInventoryUiReport,
    VendorDirectFulfillmentShipping,
    VendorInventoryReports,
    VendorSalesReports,
    XmlAllOrdersDataByOrderDataGeneral,
)
from source_amazon_seller_partner.utils import AmazonConfigException


class SourceAmazonSellerPartner(AbstractSource):
    def _get_stream_kwargs(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        endpoint, marketplace_id, _ = get_marketplaces(config.get("aws_environment"))[config.get("region")]
        auth = AWSAuthenticator(
            token_refresh_endpoint="https://api.amazon.com/auth/o2/token",
            client_id=config.get("lwa_app_id"),
            client_secret=config.get("lwa_client_secret"),
            refresh_token=config.get("refresh_token"),
            host=endpoint.replace("https://", ""),
            refresh_access_token_headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        stream_kwargs = {
            "url_base": endpoint,
            "authenticator": auth,
            "replication_start_date": config.get("replication_start_date"),
            "marketplace_id": marketplace_id,
            "period_in_days": config.get("period_in_days", 90),
            "report_options": config.get("report_options"),
            "max_wait_seconds": config.get("max_wait_seconds", 500),
            "replication_end_date": config.get("replication_end_date"),
        }
        return stream_kwargs

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
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
            self.validate_stream_report_options(config)
            stream_kwargs = self._get_stream_kwargs(config)
            orders_stream = Orders(**stream_kwargs)
            next(orders_stream.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            # Validate Orders stream without data
            if isinstance(e, StopIteration):
                return True, None

            # Additional check, since Vendor-only accounts within Amazon Seller API
            # will not pass the test without this exception
            if "403 Client Error" in str(e):
                stream_to_check = VendorSalesReports(**stream_kwargs)
                next(stream_to_check.read_records(sync_mode=SyncMode.full_refresh))
                return True, None

            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
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
        ]

        # TODO: Remove after Brand Analytics will be enabled in CLOUD:
        #  https://github.com/airbytehq/airbyte/issues/32353
        if getenv("DEPLOYMENT_MODE", "").upper() != "CLOUD":
            brand_analytics_reports = [
                BrandAnalyticsMarketBasketReports(**stream_kwargs),
                BrandAnalyticsSearchTermsReports(**stream_kwargs),
                BrandAnalyticsRepeatPurchaseReports(**stream_kwargs),
                BrandAnalyticsAlternatePurchaseReports(**stream_kwargs),
                BrandAnalyticsItemComparisonReports(**stream_kwargs),
                SellerAnalyticsSalesAndTrafficReports(**stream_kwargs),
                VendorSalesReports(**stream_kwargs),
                VendorInventoryReports(**stream_kwargs),
            ]
            streams += brand_analytics_reports

        for stream in stream_list:
            streams.append(stream(**stream_kwargs , report_options=self.get_stream_report_options(stream.name, config)))
        return streams

    def validate_stream_report_options(self, config: Mapping[str, Any]):
        if len([x.get("stream_name") for x in config.get("report_options_list", [])]) != len(
            set(x.get("stream_name") for x in config.get("report_options_list", []))
        ):
            raise AmazonConfigException(message="Stream name shuould be unique among all Report options list")
        for stream_report_option in config.get("report_options_list"):
            if len([x.get("option_name") for x in stream_report_option.get("options_list")]) != len(
                set(x.get("option_name") for x in stream_report_option.get("options_list"))
            ):
                raise AmazonConfigException(
                    message=f"Option names should be unique for `{stream_report_option.get('stream_name')}` report options"
                )

    def get_stream_report_options(self, report_name: str, config: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        if any(x for x in config.get("report_options_list", []) if x.get('stream_name') == report_name):
            return [x.get('option_list') for x in self._report_options if x.get('stream_name') == self.name][0]
        return {}
