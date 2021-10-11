#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from time import sleep

import pendulum
from airbyte_cdk.entrypoint import logger
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.common import FacebookAPIException


class MyFacebookAdsApi(FacebookAdsApi):
    """Custom Facebook API class to intercept all API calls and handle call rate limits"""

    call_rate_threshold = 90  # maximum percentage of call limit utilization
    pause_interval_minimum = pendulum.duration(minutes=1)  # default pause interval if reached or close to call rate limit

    @staticmethod
    def parse_call_rate_header(headers):
        usage = 0
        pause_interval = pendulum.duration()

        usage_header_business = headers.get("x-business-use-case-usage")
        usage_header_app = headers.get("x-app-usage")
        usage_header_ad_account = headers.get("x-ad-account-usage")

        if usage_header_ad_account:
            usage_header_ad_account_loaded = json.loads(usage_header_ad_account)
            usage = max(usage, usage_header_ad_account_loaded.get("acc_id_util_pct"))

        if usage_header_app:
            usage_header_app_loaded = json.loads(usage_header_app)
            usage = max(
                usage,
                usage_header_app_loaded.get("call_count"),
                usage_header_app_loaded.get("total_time"),
                usage_header_app_loaded.get("total_cputime"),
            )

        if usage_header_business:

            usage_header_business_loaded = json.loads(usage_header_business)
            for business_object_id in usage_header_business_loaded:
                usage_limits = usage_header_business_loaded.get(business_object_id)[0]
                usage = max(usage, usage_limits.get("call_count"), usage_limits.get("total_cputime"), usage_limits.get("total_time"))
                pause_interval = max(pause_interval, pendulum.duration(minutes=usage_limits.get("estimated_time_to_regain_access", 0)))

        return usage, pause_interval

    def handle_call_rate_limit(self, response, params):
        if "batch" in params:
            max_usage = 0
            max_pause_interval = self.pause_interval_minimum

            for record in response.json():
                headers = {header["name"].lower(): header["value"] for header in record["headers"]}
                usage, pause_interval = self.parse_call_rate_header(headers)
                max_usage = max(max_usage, usage)
                max_pause_interval = max(max_pause_interval, pause_interval)

            if max_usage > self.call_rate_threshold:
                max_pause_interval = max(max_pause_interval, self.pause_interval_minimum)
                logger.warn(f"Utilization is too high ({max_usage})%, pausing for {max_pause_interval}")
                sleep(max_pause_interval.total_seconds())
        else:
            headers = response.headers()
            usage, pause_interval = self.parse_call_rate_header(headers)
            if usage > self.call_rate_threshold or pause_interval:
                pause_interval = max(pause_interval, self.pause_interval_minimum)
                logger.warn(f"Utilization is too high ({usage})%, pausing for {pause_interval}")
                sleep(pause_interval.total_seconds())

    def call(
        self,
        method,
        path,
        params=None,
        headers=None,
        files=None,
        url_override=None,
        api_version=None,
    ):
        """Makes an API call, delegate actual work to parent class and handles call rates"""
        response = super().call(method, path, params, headers, files, url_override, api_version)
        self.handle_call_rate_limit(response, params)
        return response


class API:
    """Simple wrapper around Facebook API"""

    def __init__(self, account_id: str, access_token: str):
        self._account_id = account_id
        # design flaw in MyFacebookAdsApi requires such strange set of new default api instance
        self.api = MyFacebookAdsApi.init(access_token=access_token, crash_log=False)
        FacebookAdsApi.set_default_api(self.api)

    @cached_property
    def account(self) -> AdAccount:
        """Find current account"""
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str) -> AdAccount:
        """Actual implementation of find account"""
        try:
            accounts = fb_user.User(fbid="me").get_ad_accounts()
            for account in accounts:
                if account["account_id"] == account_id:
                    return account
        except FacebookRequestError as exc:
            raise FacebookAPIException(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        raise FacebookAPIException("Couldn't find account with id {}".format(account_id))
