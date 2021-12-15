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


from typing import Any, List, Mapping, Tuple, Union

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException
from pendulum import timezone
from pendulum.tz.timezone import Timezone

from .google_ads import GoogleAds
from .streams import Accounts, AdGroupAdReport, AdGroupAds, AdGroups, Campaigns, ClickView


class SourceGoogleAds(AbstractSource):

    def get_credentials(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config["credentials"]

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    @staticmethod
    def get_account_info(google_api) -> dict:
        return next(Accounts(api=google_api).read_records(sync_mode=None), {})

    @staticmethod
    def get_time_zone(account: dict) -> Union[timezone, str]:
        time_zone_name = account.get("customer.time_zone")
        if time_zone_name:
            return Timezone(time_zone_name)
        return "local"

    @staticmethod
    def is_manager_account(account: dict) -> bool:
        return bool(account.get("customer.manager"))

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            logger.info("Checking the config")
            google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
            account_info = self.get_account_info(google_api)

            return True, None
        except GoogleAdsException as error:
            return False, f"Unable to connect to Google Ads API with the provided credentials - {repr(error.failure)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
        account_info = self.get_account_info(google_api)
        time_zone = self.get_time_zone(account_info)
        incremental_stream_config = dict(
            api=google_api, conversion_window_days=config["conversion_window_days"], start_date=config["start_date"], time_zone=time_zone
        )

        streams = [
            AdGroupAds(api=google_api),
            AdGroups(api=google_api),
            Accounts(api=google_api),
            Campaigns(api=google_api),
            ClickView(**incremental_stream_config),
        ]

        # Metrics streams cannot be requested for a manager account.
        if not self.is_manager_account(account_info):
            streams.extend(
                [
                    AdGroupAdReport(**incremental_stream_config),
                ]
            )
        return streams
