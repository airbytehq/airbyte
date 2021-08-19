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


import json
from datetime import datetime
from typing import Dict, Generator
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from typing import Mapping, Any, Tuple, List
from airbyte_cdk.sources import AbstractSource
from .spec import SourceTikTokMarketingSpec
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .streams import PermissionStream


DOCUMENTATION_URL = "https://docs.airbyte.io/integrations/sources/tiktok-marketing"


class TiktokTokenAuthenticator(TokenAuthenticator):
    """
    Docs: https://ads.tiktok.com/marketing_api/docs?rid=sta6fe2yww&id=1701890922708994
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Access-Token": self._token}


class SourceTiktokMarketing(AbstractSource):

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration."""
        # make dummy instance of stream_class in order to get 'supports_incremental' property
        # incremental = self.stream_class(dataset="", provider="", format="", path_pattern="").supports_incremental

        # supported_dest_sync_modes = [DestinationSyncMode.overwrite]
        # if incremental:
        #     supported_dest_sync_modes.extend([DestinationSyncMode.append, DestinationSyncMode.append_dedup])

        return ConnectorSpecification(
            documentationUrl=DOCUMENTATION_URL,
            changelogUrl=DOCUMENTATION_URL,
            # supportsIncremental=incremental,
            # supported_destination_sync_modes=supported_dest_sync_modes,
            connectionSpecification=SourceTikTokMarketingSpec.schema(),
        )

    def _prepare_stream_args(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Converts an input configure to stream arguments"""
        return {
            "authenticator": TiktokTokenAuthenticator(config["access_token"]),
            "is_sandbox": config.get("is_sandbox") or False,
            "start_time": config.get("start_time") or "1970-01-01",
        }

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        ddd = PermissionStream(
            **self._prepare_stream_args(config)).get_settings()
        # Define the endpoint from user's config
        url_base = get_url_base(config["is_sandbox"])
        try:
            ZuoraAuthenticator(
                token_refresh_endpoint=f"{url_base}/oauth/token",
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                # Zuora doesn't have Refresh Token parameter.
                refresh_token=None,
            ).get_auth_header()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return []
