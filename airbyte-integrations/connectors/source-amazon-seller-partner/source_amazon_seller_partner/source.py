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
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner.auth import AWSSigV4
from source_amazon_seller_partner.constants import get_marketplaces_enum, AWS_ENV
from source_amazon_seller_partner.streams import FbaInventoryReports, FlatFileOrdersReports, MerchantListingsReports, Orders


class SourceAmazonSellerPartner(AbstractSource):
    marketplace_values = get_marketplaces_enum(AWS_ENV.PRODUCTION).US

    def _get_stream_kwargs(self, config: Mapping[str, Any]):
        self.marketplace_values = getattr(get_marketplaces_enum(getattr(AWS_ENV, config["aws_env"])), config["region"])

        boto3_client = boto3.client("sts", aws_access_key_id=config["aws_access_key"], aws_secret_access_key=config["aws_secret_key"])
        role = boto3_client.assume_role(RoleArn=config["role_arn"], RoleSessionName="guid")
        role_creds = role["Credentials"]
        auth = AWSSigV4(
            "execute-api",
            aws_access_key_id=role_creds.get("AccessKeyId"),
            aws_secret_access_key=role_creds.get("SecretAccessKey"),
            region=self.marketplace_values.region,
            aws_session_token=role_creds.get("SessionToken"),
        )
        stream_kwargs = {
            "url_base": self.marketplace_values.endpoint,
            "authenticator": auth,
            "access_token_credentials": {
                "client_id": config["lwa_app_id"],
                "client_secret": config["lwa_client_secret"],
                "refresh_token": config["refresh_token"],
            },
            "replication_start_date": config["replication_start_date"],
        }
        return stream_kwargs

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
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

        stream_kwargs = self._get_stream_kwargs(config)
        streams = [
            MerchantListingsReports(**stream_kwargs),
            FlatFileOrdersReports(**stream_kwargs),
            FbaInventoryReports(**stream_kwargs),
            Orders(marketplace_ids=self.marketplace_values.marketplace_id, **stream_kwargs),
        ]
        return streams
