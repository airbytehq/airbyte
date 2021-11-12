#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple, Type

from airbyte_cdk.models import ConnectorSpecification, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import Field
from pydantic.main import BaseModel
from source_klaviyo.streams import Campaigns, Events, GlobalExclusions, Lists, Metrics


class ConnectorConfig(BaseModel):
    class Config:
        title = "Klaviyo Spec"

    api_key: str = Field(
        description='Klaviyo API Key. See our <a href="https://docs.airbyte.io/integrations/sources/klaviyo">docs</a> if you need help finding this key.',
        airbyte_secret=True,
    )
    start_date: str = Field(
        description="UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )


class SourceKlaviyo(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK

        try:
            # we use metrics endpoint because it never return an error
            _ = list(Metrics(api_key=config.api_key).read_records(sync_mode=SyncMode.full_refresh))
            ok = True
        except Exception as e:
            error_msg = repr(e)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        return [
            Campaigns(api_key=config.api_key),
            Events(api_key=config.api_key, start_date=config.start_date),
            GlobalExclusions(api_key=config.api_key),
            Lists(api_key=config.api_key),
        ]

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/klaviyo",
            changelogUrl="https://docs.airbyte.io/integrations/sources/klaviyo",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
        )
