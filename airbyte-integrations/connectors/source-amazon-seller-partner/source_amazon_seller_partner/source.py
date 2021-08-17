#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, List, Mapping, Tuple

import boto3
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import Field
from pydantic.main import BaseModel
from source_amazon_seller_partner.auth import AWSAuthenticator, AWSSignature
from source_amazon_seller_partner.constants import AWSEnvironment, AWSRegion, get_marketplaces
from source_amazon_seller_partner.streams import FbaInventoryReports, FlatFileOrdersReports, MerchantListingsReports, Orders


class ConnectorConfig(BaseModel):
    class Config:
        title = "Amazon Seller Partner Spec"

    replication_start_date: str = Field(
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
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
    def _get_stream_kwargs(self, config: ConnectorConfig):
        self.endpoint, self.marketplace_id, self.region = get_marketplaces(config.aws_environment)[config.region]

        boto3_client = boto3.client("sts", aws_access_key_id=config.aws_access_key, aws_secret_access_key=config.aws_secret_key)
        role = boto3_client.assume_role(RoleArn=config.role_arn, RoleSessionName="guid")
        role_creds = role["Credentials"]
        aws_signature = AWSSignature(
            service="execute-api",
            aws_access_key_id=role_creds.get("AccessKeyId"),
            aws_secret_access_key=role_creds.get("SecretAccessKey"),
            aws_session_token=role_creds.get("SessionToken"),
            region=self.region,
        )
        auth = AWSAuthenticator(
            token_refresh_endpoint="https://api.amazon.com/auth/o2/token",
            client_secret=config.lwa_client_secret,
            client_id=config.lwa_app_id,
            refresh_token=config.refresh_token,
            host=self.endpoint.replace("https://", ""),
        )
        stream_kwargs = {
            "url_base": self.endpoint,
            "authenticator": auth,
            "aws_signature": aws_signature,
            "replication_start_date": config.replication_start_date,
        }
        return stream_kwargs

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            stream_kwargs = self._get_stream_kwargs(config)
            merchant_listings_reports_gen = MerchantListingsReports(**stream_kwargs).read_records(sync_mode=SyncMode.full_refresh)
            next(merchant_listings_reports_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Amazon Seller API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        stream_kwargs = self._get_stream_kwargs(config)

        return [
            MerchantListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FbaInventoryReports(**stream_kwargs),
            Orders(marketplace_ids=[self.marketplace_id], **stream_kwargs),
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
