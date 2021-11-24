#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import boto3
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
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
    VendorDirectFulfillmentShipping,
    VendorInventoryHealthReports,
)


class SourceAmazonSellerPartner(AbstractSource):
    def _get_stream_kwargs(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        endpoint, marketplace_id, region = get_marketplaces(config["aws_environment"])[config["region"]]

        boto3_client = boto3.client("sts", aws_access_key_id=config["aws_access_key"], aws_secret_access_key=config["aws_secret_key"])
        role = boto3_client.assume_role(RoleArn=config["role_arn"], RoleSessionName="guid")
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
            client_secret=config["lwa_client_secret"],
            client_id=config["lwa_app_id"],
            refresh_token=config["refresh_token"],
            host=endpoint.replace("https://", ""),
        )
        stream_kwargs = {
            "url_base": endpoint,
            "authenticator": auth,
            "aws_signature": aws_signature,
            "replication_start_date": config["replication_start_date"],
            "marketplace_ids": [marketplace_id],
        }
        return stream_kwargs

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Check connection to Amazon SP API by requesting the list of reports as this endpoint should be available for any config.
        Validate if response has the expected error code and body.
        Show error message in case of request exception or unexpected response.
        """
        try:
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
        ]
