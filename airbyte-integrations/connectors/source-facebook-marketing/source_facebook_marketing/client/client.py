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


from typing import Any, List, Mapping, Tuple

import pendulum as pendulum

# FIXME (Eugene K): register logger as standard python logger
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.sources.deprecated.client import BaseClient
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.exceptions import FacebookRequestError

from .api import AdCreativeAPI, AdsAPI, AdSetsAPI, AdsInsightAPI, CampaignAPI
from .common import FacebookAPIException


class Client(BaseClient):
    def __init__(
        self, account_id: str, access_token: str, start_date: str, include_deleted: bool = False, insights_lookback_window: int = 28
    ):
        self._account_id = account_id
        self._start_date = pendulum.parse(start_date)
        self._insights_lookback_window = insights_lookback_window

        self._api = FacebookAdsApi.init(access_token=access_token)
        self._apis = {
            "campaigns": CampaignAPI(self, include_deleted=include_deleted),
            "adsets": AdSetsAPI(self, include_deleted=include_deleted),
            "ads": AdsAPI(self, include_deleted=include_deleted),
            "adcreatives": AdCreativeAPI(self),
            "ads_insights": AdsInsightAPI(self, start_date=self._start_date, buffer_days=self._insights_lookback_window),
            "ads_insights_age_and_gender": AdsInsightAPI(
                self, start_date=self._start_date, breakdowns=["age", "gender"], buffer_days=self._insights_lookback_window
            ),
            "ads_insights_country": AdsInsightAPI(
                self, start_date=self._start_date, breakdowns=["country"], buffer_days=self._insights_lookback_window
            ),
            "ads_insights_region": AdsInsightAPI(
                self, start_date=self._start_date, breakdowns=["region"], buffer_days=self._insights_lookback_window
            ),
            "ads_insights_dma": AdsInsightAPI(
                self, start_date=self._start_date, breakdowns=["dma"], buffer_days=self._insights_lookback_window
            ),
            "ads_insights_platform_and_device": AdsInsightAPI(
                self,
                start_date=self._start_date,
                breakdowns=["publisher_platform", "platform_position", "impression_device"],
                buffer_days=self._insights_lookback_window,
            ),
        }
        super().__init__()

    def _get_fields_from_stream(self, stream: AirbyteStream) -> List[str]:
        """Use schemas from schemas folder and not from configured catalog"""
        json_schema = self._schema_loader.get_schema(stream.name)
        return list(json_schema.get("properties", {}).keys())

    def _enumerate_methods(self) -> Mapping[str, callable]:
        """Detect available streams and return mapping"""
        return {name: api.list for name, api in self._apis.items()}

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    @cached_property
    def account(self):
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str):
        try:
            accounts = fb_user.User(fbid="me").get_ad_accounts()
            for account in accounts:
                if account["account_id"] == account_id:
                    return account
        except FacebookRequestError as exc:
            raise FacebookAPIException(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        raise FacebookAPIException("Couldn't find account with id {}".format(account_id))

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_message = None
        try:
            self._find_account(self._account_id)
        except FacebookAPIException as exc:
            logger.error(str(exc))  # we might need some extra details, so log original exception here
            alive = False
            error_message = str(exc)

        return alive, error_message
