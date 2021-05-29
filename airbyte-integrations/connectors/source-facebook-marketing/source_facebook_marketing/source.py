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
from typing import Mapping, Any, Tuple, List, Type

from pydantic import BaseModel, Field
from cached_property import cached_property

from airbyte_cdk.models import ConnectorSpecification, DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.exceptions import FacebookRequestError

from source_facebook_marketing.common import FacebookAPIException
from source_facebook_marketing.streams import (
    Campaigns, AdSets, Ads, AdCreatives, AdsInsights, AdsInsightsAgeAndGender, AdsInsightsCountry,
    AdsInsightsRegion, AdsInsightsDma, AdsInsightsPlatformAndDevice
)


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Facebook Marketing"

    account_id: str = Field(
        description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API."
    )

    access_token: str = Field(
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information',
        airbyte_secret=True,
    )

    start_date: datetime = Field(
        description="The date from which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    include_deleted: bool = Field(
        default=False,
        description="Include data from deleted campaigns, ads, and adsets."
    )

    insights_lookback_window: int = Field(
        default=28,
        description="The attribution window for the actions",
        minimum=0,
        maximum=28,
    )


class API:
    def __init__(self, account_id: str, access_token: str):
        self._account_id = account_id
        self.api = FacebookAdsApi.init(access_token=access_token)

    @cached_property
    def account(self):
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str):
        try:
            accounts = fb_user.User(fbid="me").get_ad_accounts()
            for account in accounts:
                print(account)
                if account["account_id"] == account_id:
                    return account
        except FacebookRequestError as exc:
            raise FacebookAPIException(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        raise FacebookAPIException("Couldn't find account with id {}".format(account_id))


class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)

        try:
            logger.info(f"Select account {api.account}")
            ok = True
        except Exception as exc:
            logger.error(str(exc))  # we might need some extra details, so log original exception here
            error_msg = repr(exc)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)

        return [
            Campaigns(api=api, include_deleted=config.include_deleted),
            AdSets(api=api, include_deleted=config.include_deleted),
            Ads(api=api, include_deleted=config.include_deleted),
            AdCreatives(api=api),
            AdsInsights(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window),
            AdsInsightsAgeAndGender(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window,),
            AdsInsightsCountry(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window,),
            AdsInsightsRegion(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window,),
            AdsInsightsDma(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window,),
            AdsInsightsPlatformAndDevice(api=api, start_date=config.start_date, buffer_days=config.insights_lookback_window,),
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
