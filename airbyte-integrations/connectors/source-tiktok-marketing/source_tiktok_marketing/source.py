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


# from airbyte_cdk.models import (
#     AirbyteCatalog,
#     AirbyteMessage,
#     AirbyteRecordMessage,
#     AirbyteStream,
#     ConfiguredAirbyteCatalog,
#     Status,
#     Type,
# )
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .spec import SourceTikTokMarketingSpec
from .streams import AdGroups, Ads, Advertisers, Campaigns

DOCUMENTATION_URL = "https://docs.airbyte.io/integrations/sources/tiktok-marketing"


class TiktokTokenAuthenticator(TokenAuthenticator):
    """
    Docs: https://ads.tiktok.com/marketing_api/docs?rid=sta6fe2yww&id=1701890922708994
    """

    def __init__(self, token: str, **kwargs):
        super().__init__(token, **kwargs)
        self.token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Access-Token": self.token}


class SourceTiktokMarketing(AbstractSource):
    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration."""
        return ConnectorSpecification(
            documentationUrl=DOCUMENTATION_URL,
            changelogUrl=DOCUMENTATION_URL,
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=SourceTikTokMarketingSpec.schema(),
        )

    @staticmethod
    def _prepare_stream_args(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Converts an input configure to stream arguments"""
        return {
            "authenticator": TiktokTokenAuthenticator(config["access_token"]),
            "start_time": config.get("start_time") or "1970-01-01",
            "advertiser_id": config["environment"].get("advertiser_id"),
            "app_id": config["environment"].get("app_id"),
            "secret": config["environment"].get("secret"),
        }

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        try:
            next(Advertisers(**self._prepare_stream_args(config)).read_records(SyncMode.full_refresh))
        except Exception as err:
            return False, err
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self._prepare_stream_args(config)
        return [Ads(**args), Advertisers(**args), AdGroups(**args), Campaigns(**args)]
