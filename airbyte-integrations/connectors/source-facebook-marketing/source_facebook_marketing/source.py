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
from typing import Any, List, Mapping, Tuple, Type, Optional
from airbyte_cdk.entrypoint import logger

from airbyte_cdk.models import (
    ConnectorSpecification,
    DestinationSyncMode,
    AirbyteCatalog
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel, Field, Json
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import (
    AdCreatives,
    Ads,
    AdSets,
    AdsInsights,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
    Campaigns,
    CustomAdsInsights,
    CustomAdsInsightsAgeAndGender,
    CustomAdsInsightsCountry,
    CustomAdsInsightsRegion,
    CustomAdsInsightsDma,
    CustomAdsInsightsPlatformAndDevice,

)


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Facebook Marketing"

    account_id: str = Field(description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.")

    access_token: str = Field(
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information',
        airbyte_secret=True,
    )

    start_date: datetime = Field(
        description="The date from which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    include_deleted: bool = Field(default=False, description="Include data from deleted campaigns, ads, and adsets.")

    insights_lookback_window: int = Field(
        default=28,
        description="The attribution window for the actions",
        minimum=0,
        maximum=28,
    )

    insights_days_per_job: int = Field(
        default=7,
        description="Number of days to sync in one job. The more data you have - the smaller you want this parameter to be.",
        minimum=1,
        maximum=30,
    )
    custom_insights: Optional[Json] = Field(description="A json objet with custom insights")


class SourceFacebookMarketing(AbstractSource):
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
            api = API(account_id=config.account_id, access_token=config.access_token)
            logger.info(f"Select account {api.account}")
            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)
        insights_args = dict(
            api=api,
            start_date=config.start_date,
            buffer_days=config.insights_lookback_window,
            days_per_job=config.insights_days_per_job,
        )

        streams = [
            Campaigns(api=api, start_date=config.start_date, include_deleted=config.include_deleted),
            AdSets(api=api, start_date=config.start_date, include_deleted=config.include_deleted),
            Ads(api=api, start_date=config.start_date, include_deleted=config.include_deleted),
            AdCreatives(api=api),

            AdsInsights(**insights_args),
            AdsInsightsAgeAndGender(**insights_args),
            AdsInsightsCountry(**insights_args),
            AdsInsightsRegion(**insights_args),
            AdsInsightsDma(**insights_args),
            AdsInsightsPlatformAndDevice(**insights_args),
        ]

        return self._add_custom_insights_streams(insights=config.custom_insights, args=insights_args, streams=streams)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            changelogUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
        )

    def _add_custom_insights_streams(self, insights, args, streams) -> List[Type[Stream]]:
        """ Update method, returns streams plus custom streams
        After we checked if 'custom_insights_fields' exists we add the custom streams with the
        fields that we setted in the confi
        """
        insights_custom_streams = list()
        for insight_entry in insights.get('insights'):
            args['name'] = insight_entry.get('name')
            args['fields'] = insight_entry.get('fields')
            args['breakdowns'] = insight_entry.get('breakdowns')
            args['action_breakdowns'] = insight_entry.get('action_breakdowns')
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        new_streams = list()
        for stream in streams:
            if stream.name not in [e.name for e in insights_custom_streams]:
                new_streams.append(stream)

        return new_streams + insights_custom_streams
