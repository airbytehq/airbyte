#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import boto3
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import Field
from pydantic.main import BaseModel
from source_amazon_seller_partner.auth import AWSAuthenticator, AWSSignature
from source_amazon_seller_partner.constants import AWSEnvironment, AWSRegion, get_marketplaces
from source_amazon_seller_partner.streams import (
    BrandAnalyticsAlternatePurchaseReports,
    BrandAnalyticsItemComparisonReports,
    BrandAnalyticsMarketBasketReports,
    BrandAnalyticsRepeatPurchaseReports,
    BrandAnalyticsSearchTermsReports,
    FbaInventoryReports,
    FbaOrdersReports,
    FbaShipmentsReports,
    FlatFileOpenListingsReports,
    FlatFileOrdersReports,
    FlatFileOrdersReportsByLastUpdate,
    FulfilledShipmentsReports,
    MerchantListingsReports,
    Orders,
    SellerFeedbackReports,
    VendorDirectFulfillmentShipping,
    VendorInventoryHealthReports,
)


class ConnectorConfig(BaseModel):
    class Config:
        title = "Amazon Seller Partner Spec"

    replication_start_date: str = Field(
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        title="Start Date",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )
    period_in_days: int = Field(
        30,
        description="Will be used for stream slicing for initial full_refresh sync when no updated state is present for reports that support sliced incremental sync.",
        examples=["30", "365"],
    )
    report_options: str = Field(
        None,
        description="Additional information passed to reports. This varies by report type. Must be a valid json string.",
        examples=['{"GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT": {"reportPeriod": "WEEK"}}', '{"GET_SOME_REPORT": {"custom": "true"}}'],
    )
    max_wait_seconds: int = Field(
        500,
        title="Max wait time for reports (in seconds)",
        description="Sometimes report can take up to 30 minutes to generate. This will set the limit for how long to wait for a successful report.",
        examples=["500", "1980"],
    )
    refresh_token: str = Field(
        description="The Refresh Token obtained via OAuth flow authorization.",
        title="Refresh Token",
        airbyte_secret=True,
    )
    lwa_app_id: str = Field(description="Your Login with Amazon App ID", title="LwA App Id", airbyte_secret=True)
    lwa_client_secret: str = Field(description="Your Login with Amazon Client Secret.", title="LwA Client Secret", airbyte_secret=True)
    aws_access_key: str = Field(
        description="Specifies the AWS access key used as part of the credentials to authenticate the user.",
        title="AWS Access Key",
        airbyte_secret=True,
    )
    aws_secret_key: str = Field(
        description="Specifies the AWS secret key used as part of the credentials to authenticate the user.",
        title="AWS Secret Access Key",
        airbyte_secret=True,
    )
    role_arn: str = Field(
        description="Specifies the Amazon Resource Name (ARN) of an IAM role that you want to use to perform operations requested using this profile. (Needs permission to 'Assume Role' STS).",
        title="Role ARN",
        airbyte_secret=True,
    )
    aws_environment: AWSEnvironment = Field(description="Select the AWS Environment.", title="AWS Environment")
    region: AWSRegion = Field(description="Select the AWS Region.", title="AWS Region")


class SourceAmazonSellerPartner(AbstractSource):
    def _get_stream_kwargs(self, config: ConnectorConfig) -> Mapping[str, Any]:
        endpoint, marketplace_id, region = get_marketplaces(config.aws_environment)[config.region]

        boto3_client = boto3.client("sts", aws_access_key_id=config.aws_access_key, aws_secret_access_key=config.aws_secret_key)
        role = boto3_client.assume_role(RoleArn=config.role_arn, RoleSessionName="guid")
        role_creds = role["Credentials"]
        aws_signature = AWSSignature(
            service="execute-api",
            aws_access_key_id=role_creds.get("AccessKeyId"),
            aws_secret_access_key=role_creds.get("SecretAccessKey"),
            aws_session_token=role_creds.get("SessionToken"),
            region=region,
        )
        auth = AWSAuthenticator(
            token_refresh_endpoint="https://api.amazon.com/auth/o2/token",
            client_secret=config.lwa_client_secret,
            client_id=config.lwa_app_id,
            refresh_token=config.refresh_token,
            host=endpoint.replace("https://", ""),
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
        }
        return stream_kwargs

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Check connection to Amazon SP API by requesting the list of reports as this endpoint should be available for any config.
        Validate if response has the expected error code and body.
        Show error message in case of request exception or unexpected response.
        """
        try:
            config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            stream_kwargs = self._get_stream_kwargs(config)
            orders_stream = Orders(**stream_kwargs)
            next(orders_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except StopIteration or requests.exceptions.RequestException as e:
            if isinstance(e, StopIteration):
                e = "Could not check connection without data for Orders stream. " "Please change value for replication start date field."

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        stream_kwargs = self._get_stream_kwargs(config)

        return [
            FbaInventoryReports(**stream_kwargs),
            FbaOrdersReports(**stream_kwargs),
            FbaShipmentsReports(**stream_kwargs),
            FlatFileOpenListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FlatFileOrdersReportsByLastUpdate(**stream_kwargs),
            FulfilledShipmentsReports(**stream_kwargs),
            MerchantListingsReports(**stream_kwargs),
            VendorDirectFulfillmentShipping(**stream_kwargs),
            VendorInventoryHealthReports(**stream_kwargs),
            Orders(**stream_kwargs),
            SellerFeedbackReports(**stream_kwargs),
            BrandAnalyticsMarketBasketReports(**stream_kwargs),
            BrandAnalyticsSearchTermsReports(**stream_kwargs),
            BrandAnalyticsRepeatPurchaseReports(**stream_kwargs),
            BrandAnalyticsAlternatePurchaseReports(**stream_kwargs),
            BrandAnalyticsItemComparisonReports(**stream_kwargs),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required
        configurations (e.g: username and password) required to run this integration.
        """
        # FIXME: airbyte-cdk does not parse pydantic $ref correctly. This override won't be needed after the fix
        schema = ConnectorConfig.schema()
        schema["properties"]["aws_environment"] = schema["definitions"]["AWSEnvironment"]
        schema["properties"]["region"] = schema["definitions"]["AWSRegion"]

        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/amazon-seller-partner",
            changelogUrl="https://docs.airbyte.io/integrations/sources/amazon-seller-partner",
            connectionSpecification=schema,
        )
