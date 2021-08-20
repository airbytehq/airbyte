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

from datetime import datetime
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel, Field
from source_instagram.api import InstagramAPI
from source_instagram.streams import Media, MediaInsights, Stories, StoryInsights, UserInsights, UserLifetimeInsights, Users


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Instagram"

    start_date: datetime = Field(
        description="The date from which you'd like to replicate data for User Insights, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    access_token: str = Field(
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/instagram">docs</a> for more information',
        airbyte_secret=True,
    )


class SourceInstagram(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None

        try:
            config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            api = InstagramAPI(access_token=config.access_token)
            logger.info(f"Available accounts: {api.accounts}")
            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:
        for stream in self.streams(config):
            state_key = str(stream.name)
            if state and state_key in state and hasattr(stream, "upgrade_state_to_latest_format"):
                state[state_key] = stream.upgrade_state_to_latest_format(state[state_key])
        return super().read(logger, config, catalog, state)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = InstagramAPI(access_token=config.access_token)

        return [
            Media(api=api),
            MediaInsights(api=api),
            Stories(api=api),
            StoryInsights(api=api),
            Users(api=api),
            UserLifetimeInsights(api=api),
            UserInsights(api=api, start_date=config.start_date),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/instagram",
            changelogUrl="https://docs.airbyte.io/integrations/sources/instagram",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
        )
