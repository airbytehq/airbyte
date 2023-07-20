#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import boto3
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner.auth import AWSAuthenticator, AWSSignature
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
    FbaFulfillmentCurrentInventoryReport,
    FbaFulfillmentCustomerShipmentPromotionReport,
    FbaFulfillmentInventoryAdjustReport,
    FbaFulfillmentInventoryReceiptsReport,
    FbaFulfillmentInventorySummaryReport,
    FbaFulfillmentMonthlyInventoryReport,
    FbaInventoryPlaningReport,
    FbaMyiUnsuppressedInventoryReport,
    FbaOrdersReports,
    FbaReimbursementsReports,
    FbaReplacementsReports,
    FbaShipmentsReports,
    FbaSnsForecastReport,
    FbaSnsPerformanceReport,
    FbaStorageFeesReports,
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
        endpoint, marketplace_id, region = get_marketplaces(config.get("aws_environment"))[config.get("region")]

        sts_credentials = self.get_sts_credentials(config)
        role_creds = sts_credentials["Credentials"]
        aws_signature = AWSSignature(
            service="execute-api",
            aws_access_key_id=role_creds.get("AccessKeyId"),
            aws_secret_access_key=role_creds.get("SecretAccessKey"),
            aws_session_token=role_creds.get("SessionToken"),
            region=region,
        )
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
            "aws_signature": aws_signature,
            "replication_start_date": config.get("replication_start_date"),
            "marketplace_id": marketplace_id,
            "period_in_days": config.get("period_in_days", 90),
            "report_options": config.get("report_options"),
            "max_wait_seconds": config.get("max_wait_seconds", 500),
            "replication_end_date": config.get("replication_end_date"),
            "advanced_stream_options": config.get("advanced_stream_options"),
        }
        return stream_kwargs

    @staticmethod
    def get_sts_credentials(config: Mapping[str, Any]) -> dict:
        """
        We can only use a IAM User arn entity or a IAM Role entity.
        If we use an IAM user arn entity in the connector configuration we need to get the credentials directly from the boto3 sts client
        If we use an IAM role arn entity we need to invoke the assume_role from the boto3 sts client to get the credentials related to that role

        :param config:
        """
        boto3_client = boto3.client(
            "sts", aws_access_key_id=config.get("aws_access_key"), aws_secret_access_key=config.get("aws_secret_key")
        )
        *_, arn_resource = config.get("role_arn").split(":")
        if arn_resource.startswith("user"):
            sts_credentials = boto3_client.get_session_token()
        elif arn_resource.startswith("role"):
            sts_credentials = boto3_client.assume_role(RoleArn=config.get("role_arn"), RoleSessionName="guid")
        else:
            raise ValueError("Invalid ARN, your ARN is not for a user or a role")
        return sts_credentials

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
            stream_to_check = VendorSalesReports(**stream_kwargs)
            next(stream_to_check.read_records(sync_mode=SyncMode.full_refresh))

            return True, None
        except Exception as e:
            # Validate Orders stream without data
            if isinstance(e, StopIteration):
                return True, None

            # Additional check, since Vendor-ony accounts within Amazon Seller API will not pass the test without this exception
            if "403 Client Error" in str(e):
                return True, None

            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        stream_kwargs = self._get_stream_kwargs(config)

        return [
            FbaCustomerReturnsReports(**stream_kwargs),
            FbaAfnInventoryReports(**stream_kwargs),
            FbaAfnInventoryByCountryReports(**stream_kwargs),
            FbaOrdersReports(**stream_kwargs),
            FbaShipmentsReports(**stream_kwargs),
            FbaReplacementsReports(**stream_kwargs),
            FbaStorageFeesReports(**stream_kwargs),
            RestockInventoryReports(**stream_kwargs),
            FlatFileOpenListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FlatFileOrdersReportsByLastUpdate(**stream_kwargs),
            FlatFileSettlementV2Reports(**stream_kwargs),
            FulfilledShipmentsReports(**stream_kwargs),
            MerchantListingsReports(**stream_kwargs),
            VendorDirectFulfillmentShipping(**stream_kwargs),
            VendorInventoryReports(**stream_kwargs),
            VendorSalesReports(**stream_kwargs),
            Orders(**stream_kwargs),
            SellerAnalyticsSalesAndTrafficReports(**stream_kwargs),
            SellerFeedbackReports(**stream_kwargs),
            BrandAnalyticsMarketBasketReports(**stream_kwargs),
            BrandAnalyticsSearchTermsReports(**stream_kwargs),
            BrandAnalyticsRepeatPurchaseReports(**stream_kwargs),
            BrandAnalyticsAlternatePurchaseReports(**stream_kwargs),
            BrandAnalyticsItemComparisonReports(**stream_kwargs),
            GetXmlBrowseTreeData(**stream_kwargs),
            ListFinancialEventGroups(**stream_kwargs),
            ListFinancialEvents(**stream_kwargs),
            LedgerDetailedViewReports(**stream_kwargs),
            FbaEstimatedFbaFeesTxtReport(**stream_kwargs),
            FbaFulfillmentCurrentInventoryReport(**stream_kwargs),
            FbaFulfillmentCustomerShipmentPromotionReport(**stream_kwargs),
            FbaFulfillmentInventoryAdjustReport(**stream_kwargs),
            FbaFulfillmentInventoryReceiptsReport(**stream_kwargs),
            FbaFulfillmentInventorySummaryReport(**stream_kwargs),
            FbaMyiUnsuppressedInventoryReport(**stream_kwargs),
            MerchantCancelledListingsReport(**stream_kwargs),
            MerchantListingsReport(**stream_kwargs),
            MerchantListingsReportBackCompat(**stream_kwargs),
            MerchantListingsInactiveData(**stream_kwargs),
            StrandedInventoryUiReport(**stream_kwargs),
            XmlAllOrdersDataByOrderDataGeneral(**stream_kwargs),
            FbaFulfillmentMonthlyInventoryReport(**stream_kwargs),
            MerchantListingsFypReport(**stream_kwargs),
            FbaSnsForecastReport(**stream_kwargs),
            FbaSnsPerformanceReport(**stream_kwargs),
            FlatFileArchivedOrdersDataByOrderDate(**stream_kwargs),
            FlatFileReturnsDataByReturnDate(**stream_kwargs),
            FbaInventoryPlaningReport(**stream_kwargs),
            LedgerSummaryViewReport(**stream_kwargs),
            FbaReimbursementsReports(**stream_kwargs),
        ]
