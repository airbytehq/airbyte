#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple, Type

import pendulum
import requests
from airbyte_cdk.models import AuthSpecification, ConnectorSpecification, DestinationSyncMode, OAuth2Specification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_facebook_marketing.api import API
from source_facebook_marketing.spec import ConnectorConfig, InsightConfig
from source_facebook_marketing.streams import (
    Activities,
    AdAccount,
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
    Images,
    Videos,
)

from .utils import validate_end_date, validate_start_date

logger = logging.getLogger("airbyte")


class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, _logger: "logging.Logger", config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param _logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config = ConnectorConfig.parse_obj(config)
        if pendulum.instance(config.end_date) < pendulum.instance(config.start_date):
            raise ValueError("end_date must be equal or after start_date.")
        try:
            api = API(account_id=config.account_id, access_token=config.access_token)
            logger.info(f"Select account {api.account}")
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of the stream instances
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)

        config.start_date = validate_start_date(config.start_date)
        config.end_date = validate_end_date(config.start_date, config.end_date)

        api = API(account_id=config.account_id, access_token=config.access_token)

        insights_args = dict(
            api=api, start_date=config.start_date, end_date=config.end_date, insights_lookback_window=config.insights_lookback_window
        )
        streams = [
            AdAccount(api=api),
            AdSets(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Ads(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            AdCreatives(
                api=api,
                fetch_thumbnail_images=config.fetch_thumbnail_images,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            AdsInsights(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsAgeAndGender(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsCountry(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsRegion(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsDma(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsPlatformAndDevice(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsActionType(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            Campaigns(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Images(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Videos(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Activities(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
        ]

        return self._update_insights_streams(insights=config.custom_insights, default_args=insights_args, streams=streams)

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

    def _update_insights_streams(self, insights: List[InsightConfig], default_args, streams) -> List[Type[Stream]]:
        """Update method, if insights have values returns streams replacing the
        default insights streams else returns streams
        """
        if not insights:
            return streams

        insights_custom_streams = list()

        for insight in insights:
            args = dict(
                api=default_args["api"],
                name=f"Custom{insight.name}",
                fields=list(set(insight.fields)),
                breakdowns=list(set(insight.breakdowns)),
                action_breakdowns=list(set(insight.action_breakdowns)),
                time_increment=insight.time_increment,
                start_date=insight.start_date or default_args["start_date"],
                end_date=insight.end_date or default_args["end_date"],
                insights_lookback_window=insight.insights_lookback_window or default_args["insights_lookback_window"],
            )
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams
