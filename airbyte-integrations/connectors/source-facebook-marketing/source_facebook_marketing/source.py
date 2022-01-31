#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple, Type

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    AuthSpecification,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    OAuth2Specification,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from source_facebook_marketing.api import API
from source_facebook_marketing.spec import ConnectorConfig
from source_facebook_marketing.streams import (
    AdCreatives,
    Ads,
    AdSets,
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
    Campaigns,
    Videos,
)

logger = logging.getLogger("airbyte")


class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, _logger: "logging.Logger", config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param _logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config = ConnectorConfig.parse_obj(config)
        api = API(account_id=config.account_id, access_token=config.access_token)
        logger.info(f"Select account {api.account}")

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of the stream instances
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)
        api = API(account_id=config.account_id, access_token=config.access_token)

        insights_args = dict(
            api=api,
            start_date=config.start_date,
            end_date=config.end_date,
        )

        streams = [
            Campaigns(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdSets(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            Ads(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdCreatives(api=api, fetch_thumbnail_images=config.fetch_thumbnail_images),
            AdsInsights(**insights_args),
            AdsInsightsAgeAndGender(**insights_args),
            AdsInsightsCountry(**insights_args),
            AdsInsightsRegion(**insights_args),
            AdsInsightsDma(**insights_args),
            AdsInsightsPlatformAndDevice(**insights_args),
            AdsInsightsActionType(**insights_args),
            Videos(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
        ]

        return self._update_insights_streams(insights=config.custom_insights, args=insights_args, streams=streams)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration.
        The spec is a JSON-Schema object describing the required configurations
        (e.g: username and password) required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            changelogUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
            authSpecification=AuthSpecification(
                auth_type="oauth2.0",
                oauth2Specification=OAuth2Specification(
                    rootObject=[], oauthFlowInitParameters=[], oauthFlowOutputParameters=[["access_token"]]
                ),
            ),
        )

    def _update_insights_streams(self, insights, args, streams) -> List[Type[Stream]]:
        """Update method, if insights have values returns streams replacing the
        default insights streams else returns streams
        """
        if not insights:
            return streams

        insights_custom_streams = list()

        for insight in insights:
            args["name"] = f"Custom{insight.name}"
            args["fields"] = list(set(insight.fields))
            args["breakdowns"] = list(set(insight.breakdowns))
            args["action_breakdowns"] = list(set(insight.action_breakdowns))
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams
