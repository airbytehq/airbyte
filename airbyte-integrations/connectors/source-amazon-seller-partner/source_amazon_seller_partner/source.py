#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from os import getenv
from typing import Any, List, Mapping, Tuple

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
            "replication_end_date": config.get("replication_end_date"),
            "advanced_stream_options": config.get("advanced_stream_options"),
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
        stream_kwargs = self._get_stream_kwargs(config)
        streams = [
            FbaCustomerReturnsReports(**stream_kwargs),
            FbaAfnInventoryReports(**stream_kwargs),
            FbaAfnInventoryByCountryReports(**stream_kwargs),
            FbaOrdersReports(**stream_kwargs),
            FbaShipmentsReports(**stream_kwargs),
            FbaReplacementsReports(**stream_kwargs),
            FbaStorageFeesReports(**stream_kwargs),
            RestockInventoryReports(**stream_kwargs),
            FlatFileActionableOrderDataShipping(**stream_kwargs),
            FlatFileOpenListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FlatFileOrdersReportsByLastUpdate(**stream_kwargs),
            FlatFileSettlementV2Reports(**stream_kwargs),
            FulfilledShipmentsReports(**stream_kwargs),
            MerchantListingsReports(**stream_kwargs),
            VendorDirectFulfillmentShipping(**stream_kwargs),
            Orders(**stream_kwargs),
            OrderItems(**stream_kwargs),
            OrderReportDataShipping(**stream_kwargs),
            SellerFeedbackReports(**stream_kwargs),
            GetXmlBrowseTreeData(**stream_kwargs),
            ListFinancialEventGroups(**stream_kwargs),
            ListFinancialEvents(**stream_kwargs),
            LedgerDetailedViewReports(**stream_kwargs),
            FbaEstimatedFbaFeesTxtReport(**stream_kwargs),
            FbaFulfillmentCustomerShipmentPromotionReport(**stream_kwargs),
            FbaMyiUnsuppressedInventoryReport(**stream_kwargs),
            MerchantCancelledListingsReport(**stream_kwargs),
            MerchantListingsReport(**stream_kwargs),
            MerchantListingsReportBackCompat(**stream_kwargs),
            MerchantListingsInactiveData(**stream_kwargs),
            StrandedInventoryUiReport(**stream_kwargs),
            XmlAllOrdersDataByOrderDataGeneral(**stream_kwargs),
            MerchantListingsFypReport(**stream_kwargs),
            FbaSnsForecastReport(**stream_kwargs),
            FbaSnsPerformanceReport(**stream_kwargs),
            FlatFileArchivedOrdersDataByOrderDate(**stream_kwargs),
            FlatFileReturnsDataByReturnDate(**stream_kwargs),
            FbaInventoryPlaningReport(**stream_kwargs),
            LedgerSummaryViewReport(**stream_kwargs),
            FbaReimbursementsReports(**stream_kwargs),
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
        return streams
