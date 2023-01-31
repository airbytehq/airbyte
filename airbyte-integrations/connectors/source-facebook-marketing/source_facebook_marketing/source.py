#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple, Type
from datetime import datetime
import pendulum
import requests
from airbyte_cdk.models import AuthSpecification, ConnectorSpecification, DestinationSyncMode, OAuth2Specification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_facebook_marketing.api import API
from source_facebook_marketing.spec import ConnectorConfig, InsightConfig, ProxyConfig
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

from .utils import xor
from json import loads as json_loads
logger = logging.getLogger("airbyte")


class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, _logger: "logging.Logger", config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param _logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config: ConnectorConfig = self.transform_config_dates(
            ConnectorConfig.parse_obj(config))

        try:
            api = API(
                account_id=config.account_id,
                access_token=config.access_token,
                proxies=self.get_proxies_from_config(config)
            )
            logger.info(f"Select account {api.account}")
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    @staticmethod
    def transform_config_dates(config: ConnectorConfig) -> ConnectorConfig:

        if config.start_date and config.end_date and config.last_n_days:
            raise ValueError(
                "You must specify either Last N Days or Start Date + End Date. If you specify none of this fields, last 5 days will be used.")

        if not config.last_n_days and not config.start_date and not config.end_date:
            config.last_n_days = 5
        if xor(config.start_date, config.end_date) and config.last_n_days:
            print('xor')
            raise ValueError(
                'You must specify either Last N Days or Start Date + End Date. If you specify none of this fields, last 5 days will be used.')

        if config.last_n_days:
            config.end_date = datetime.fromisoformat(
                pendulum.today("UTC").to_iso8601_string()[:-1])
            config.start_date = datetime.fromisoformat(pendulum.instance(
                config.end_date).subtract(days=config.last_n_days).to_iso8601_string()[:-1])
        else:
            config.end_date = datetime.strptime(
                config.end_date, '%Y-%m-%dT%H:%M:%SZ')
            config.start_date = datetime.strptime(
                config.start_date, '%Y-%m-%dT%H:%M:%SZ')
            if pendulum.instance(config.end_date) < pendulum.instance(config.start_date):
                raise ValueError("end_date must be equal or after start_date.")
        print(config)
        return config

    @staticmethod
    def get_proxies_from_config(config: ConnectorConfig):
        proxies = None
        if isinstance(config.proxy, ProxyConfig):
            proxies_auth = ''
            if config.proxy.login and config.proxy.password:
                proxies_auth = f'{config.proxy.login}:{config.proxy.password}@'
            proxies = {
                config.proxy.protocol: f'{config.proxy.protocol}://{proxies_auth}{config.proxy.host}:{config.proxy.port}'
            }
        return proxies

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of the stream instances
        """
        config: ConnectorConfig = self.transform_config_dates(
            ConnectorConfig.parse_obj(config))

        proxies = self.get_proxies_from_config(config)

        api = API(
            account_id=config.account_id,
            access_token=config.access_token,
            proxies=proxies,
        )

        insights_args = dict(
            api=api, start_date=config.start_date, end_date=config.end_date, insights_lookback_window=config.insights_lookback_window
        )
        constants_args = {
            "product_name": config.product_name,
            "client_name": config.client_name,
            "custom_constants": json_loads(config.custom_json)
        }

        streams = [
            AdAccount(api=api, **constants_args,),
            AdSets(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args,
            ),
            Ads(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args
            ),
            AdCreatives(api=api, fetch_thumbnail_images=config.fetch_thumbnail_images,
                        page_size=config.page_size, **constants_args),
            AdsInsights(page_size=config.page_size, **
                        constants_args, **insights_args,),
            AdsInsightsAgeAndGender(
                page_size=config.page_size, **constants_args, **insights_args),
            AdsInsightsCountry(page_size=config.page_size, **
                               constants_args, **insights_args),
            AdsInsightsRegion(page_size=config.page_size, **
                              constants_args, **insights_args),
            AdsInsightsDma(page_size=config.page_size, **
                           constants_args, **insights_args),
            AdsInsightsPlatformAndDevice(
                page_size=config.page_size, **constants_args, **insights_args),
            AdsInsightsActionType(page_size=config.page_size,
                                  **constants_args, **insights_args),
            Campaigns(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args,
            ),
            Images(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args,
            ),
            Videos(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args,
            ),
            Activities(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                **constants_args,
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
                    rootObject=[], oauthFlowInitParameters=[
                    ], oauthFlowOutputParameters=[["access_token"]]
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
                insights_lookback_window=insight.insights_lookback_window or default_args[
                    "insights_lookback_window"],
            )
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams
