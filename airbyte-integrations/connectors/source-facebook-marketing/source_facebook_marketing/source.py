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
from typing import Any, List, Mapping, Tuple, Type

from airbyte_cdk.models import ConnectorSpecification, DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from pydantic import BaseModel, Field
from source_facebook_marketing.api import API
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

        return [
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
            AdsInsightsActionType(**insights_args),
        ]

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
