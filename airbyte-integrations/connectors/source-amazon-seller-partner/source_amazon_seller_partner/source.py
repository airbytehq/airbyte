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
    FbaInventoryReports,
    FbaOrdersReports,
    FbaShipmentsReports,
    FlatFileOpenListingsReports,
    FlatFileOrdersReports,
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
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )
    period_in_days: int = Field(
        30,
        description="Will be used for stream slicing for initial full_refresh sync when no updated state is present for reports that support sliced incremental sync.",
        examples=["30", "365"],
    )
    refresh_token: str = Field(
        description="The refresh token used obtained via authorization (can be passed to the client instead)", airbyte_secret=True
    )
    lwa_app_id: str = Field(description="Your login with amazon app id", airbyte_secret=True)
    lwa_client_secret: str = Field(description="Your login with amazon client secret", airbyte_secret=True)
    aws_access_key: str = Field(description="AWS user access key", airbyte_secret=True)
    aws_secret_key: str = Field(description="AWS user secret key", airbyte_secret=True)
    role_arn: str = Field(description="The role's arn (needs permission to 'Assume Role' STS)", airbyte_secret=True)
    aws_environment: AWSEnvironment = Field(
        description="Affects the AWS base url to be used",
    )
    region: AWSRegion = Field(description="Region to pull data from")


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
            "marketplace_ids": [marketplace_id],
            "period_in_days": config.period_in_days,
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
            FulfilledShipmentsReports(**stream_kwargs),
            MerchantListingsReports(**stream_kwargs),
            VendorDirectFulfillmentShipping(**stream_kwargs),
            VendorInventoryHealthReports(**stream_kwargs),
            Orders(**stream_kwargs),
            SellerFeedbackReports(**stream_kwargs),
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
