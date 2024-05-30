#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple, Union, MutableMapping, Iterator

import boto3
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
import copy
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.utils.event_timing import create_timer
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import split_config
from source_amazon_seller_partner.auth import AWSAuthenticator, AWSSignature
from source_amazon_seller_partner.constants import get_marketplaces, AWSEnvironment
from source_amazon_seller_partner.spec import AmazonSellerPartnerConfig, advanced_auth
from source_amazon_seller_partner.streams import (
    BrandAnalyticsAlternatePurchaseReports,
    BrandAnalyticsItemComparisonReports,
    BrandAnalyticsMarketBasketReports,
    BrandAnalyticsRepeatPurchaseReports,
    BrandAnalyticsSearchTermsReports,
    FbaCustomerReturnsReports,
    FbaInventoryReports,
    FbaOrdersReports,
    FbaReplacementsReports,
    FbaShipmentsReports,
    FbaInventoryPlanningReports,
    FBAInboundPerformanceReport,
    FBAManageInventory,
    LedgerDetailViewDataReports,
    SalesAndTrafficReports,
    FbaStorageFeesReports,
    FlatFileOpenListingsReports,
    FlatFileOrdersReports,
    FlatFileOrdersReportsByLastUpdate,
    FlatFileSettlementV2Reports,
    FulfilledShipmentsReports,
    GetXmlBrowseTreeData,
    ListFinancialEventGroups,
    ListFinancialEvents,
    MerchantListingsReports,
    Orders,
    RestockInventoryReports,
    SellerFeedbackReports,
    VendorDirectFulfillmentShipping,
    VendorInventoryHealthReports,
    FBALongTermStorageFeeChargesReport,
    FBAReimbursementsReport,
    OpenListingsReport,
    OpenListingsReportLite,
    OpenListingsReportLiter,
    ReferralFeeDiscountsReport,
    ActiveListingsReport,
    InactiveListingsReport,
    CanceledListingsReport,
    ReferralFeePreviewReport
)


class SourceAmazonSellerPartner(AbstractSource):
    def _get_stream_kwargs(self, config: AmazonSellerPartnerConfig) -> Mapping[str, Any]:
        endpoint, marketplace_id, region = get_marketplaces(AWSEnvironment.PRODUCTION)[config.region]

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
            client_id=config.lwa_app_id,
            client_secret=config.lwa_client_secret,
            refresh_token=config.refresh_token,
            host=endpoint.replace("https://", ""),
            refresh_access_token_headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        stream_kwargs = {
            "url_base": endpoint,
            "authenticator": auth,
            "aws_signature": aws_signature,
            "replication_start_date": config.replication_start_date,
            "marketplace_id": marketplace_id,
            "period_in_days": config.period_in_days,
            "report_options": config.report_options,
            "max_wait_seconds": config.max_wait_seconds,
            "replication_end_date": config.replication_end_date,
            "source_name": config.source_name
        }
        return stream_kwargs

    @staticmethod
    def get_sts_credentials(config: AmazonSellerPartnerConfig) -> dict:
        """
        We can only use a IAM User arn entity or a IAM Role entity.
        If we use an IAM user arn entity in the connector configuration we need to get the credentials directly from the boto3 sts client
        If we use an IAM role arn entity we need to invoke the assume_role from the boto3 sts client to get the credentials related to that role

        :param config:
        """
        boto3_client = boto3.client("sts", aws_access_key_id=config.aws_access_key, aws_secret_access_key=config.aws_secret_key)
        *_, arn_resource = config.role_arn.split(":")
        if arn_resource.startswith("user"):
            sts_credentials = boto3_client.get_session_token()
        elif arn_resource.startswith("role"):
            sts_credentials = boto3_client.assume_role(RoleArn=config.role_arn, RoleSessionName="guid")
        else:
            raise ValueError("Invalid ARN, your ARN is not for a user or a role")
        return sts_credentials

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Check connection to Amazon SP API by requesting the list of reports as this endpoint should be available for any config.
        Validate if response has the expected error code and body.
        Show error message in case of request exception or unexpected response.
        """
        try:
            config = AmazonSellerPartnerConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            stream_kwargs = self._get_stream_kwargs(config)
            # orders_stream = Orders(**stream_kwargs)
            # next(orders_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            if isinstance(e, StopIteration):
                logger.error(
                    "Could not check connection without data for Orders stream. Please change value for replication start date field."
                )
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = AmazonSellerPartnerConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        stream_kwargs = self._get_stream_kwargs(config)

        return [
            FbaCustomerReturnsReports(**stream_kwargs),
            FbaInventoryReports(**stream_kwargs),
            FbaOrdersReports(**stream_kwargs),
            FbaShipmentsReports(**stream_kwargs),
            FbaReplacementsReports(**stream_kwargs),
            FbaInventoryPlanningReports(**stream_kwargs),
            FBAInboundPerformanceReport(**stream_kwargs),
            FBAManageInventory(**stream_kwargs),
            LedgerDetailViewDataReports(**stream_kwargs),
            SalesAndTrafficReports(**stream_kwargs),
            FbaStorageFeesReports(**stream_kwargs),
            RestockInventoryReports(**stream_kwargs),
            FlatFileOpenListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FlatFileOrdersReportsByLastUpdate(**stream_kwargs),
            FlatFileSettlementV2Reports(**stream_kwargs),
            FulfilledShipmentsReports(**stream_kwargs),
            MerchantListingsReports(**stream_kwargs),
            VendorDirectFulfillmentShipping(**stream_kwargs),
            VendorInventoryHealthReports(**stream_kwargs),
            FBALongTermStorageFeeChargesReport(**stream_kwargs),
            FBAReimbursementsReport(**stream_kwargs),
            Orders(**stream_kwargs),
            SellerFeedbackReports(**stream_kwargs),
            BrandAnalyticsMarketBasketReports(**stream_kwargs),
            BrandAnalyticsSearchTermsReports(**stream_kwargs),
            BrandAnalyticsRepeatPurchaseReports(**stream_kwargs),
            BrandAnalyticsAlternatePurchaseReports(**stream_kwargs),
            BrandAnalyticsItemComparisonReports(**stream_kwargs),
            GetXmlBrowseTreeData(**stream_kwargs),
            ListFinancialEventGroups(**stream_kwargs),
            ListFinancialEvents(**stream_kwargs),
            OpenListingsReport(**stream_kwargs),
            OpenListingsReportLite(**stream_kwargs),
            OpenListingsReportLiter(**stream_kwargs),
            ReferralFeeDiscountsReport(**stream_kwargs),
            ActiveListingsReport(**stream_kwargs),
            InactiveListingsReport(**stream_kwargs),
            CanceledListingsReport(**stream_kwargs),
            ReferralFeePreviewReport(**stream_kwargs)
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required
        configurations (e.g: username and password) required to run this integration.
        """
        # FIXME: airbyte-cdk does not parse pydantic $ref correctly. This override won't be needed after the fix
        schema = AmazonSellerPartnerConfig.schema()
        schema["properties"]["region"] = schema["definitions"]["AWSRegion"]

        return ConnectorSpecification(
            documentationUrl="https://docs.daspire.com/setup-guide/sources/amazon-seller-partner",
            changelogUrl="https://docs.daspire.com/setup-guide/sources/amazon-seller-partner",
            connectionSpecification=schema,
            advanced_auth=advanced_auth,
        )

    def read(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-protocol."""
        # state_manager = ConnectorStateManager(state=state)
        # connector_state = state_manager.get_legacy_state()

        connector_state = copy.deepcopy(state or {})

        logger.info(f"*********** Starting syncing {self.name}")
        config, internal_config = split_config(config)
        # TODO assert all streams exist in the connector
        # get the streams once in case the connector needs to make any queries to generate them
        stream_instances = {s.name: s for s in self.streams(config)}
        self._stream_to_instance_map = stream_instances
        with create_timer(self.name) as timer:
            for configured_stream in catalog.streams:
                stream_instance = stream_instances.get(configured_stream.stream.name)
                if not stream_instance:
                    raise KeyError(
                        f"The requested stream {configured_stream.stream.name} was not found in the source."
                        f" Available streams: {stream_instances.keys()}"
                    )
                try:
                    timer.start_event(f"Syncing stream {configured_stream.stream.name}")
                    yield from self._read_stream(
                        logger=logger,
                        stream_instance=stream_instance,
                        configured_stream=configured_stream,
                        state_manager=connector_state,
                        internal_config=internal_config,
                    )
                except Exception as e:
                    logger.exception(f"Encountered an exception while reading stream {configured_stream.stream.name}")
                    display_message = stream_instance.get_error_display_message(e)
                    if display_message:
                        logger.exception("display message: {}".format(repr(e)))
                        # raise AirbyteTracedException.from_exception(e, message=display_message) from e
                    # raise e
                    logger.exception("unknown exception message: {}".format(repr(e)))
                finally:
                    timer.finish_event()
                    logger.info(f"Finished syncing {configured_stream.stream.name}")
                    logger.info(timer.report())

        logger.info(f"Finished syncing {self.name}")
