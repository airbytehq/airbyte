#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import dataclass
from time import sleep

import backoff
import pendulum
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookResponse
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.streams.common import retry_pattern, FACEBOOK_CONNECTION_RESET_ERROR_CODE

logger = logging.getLogger("airbyte")


class FacebookAPIException(Exception):
    """General class for all API errors"""


backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=120)


class MyFacebookAdsApi(FacebookAdsApi):
    """Custom Facebook API class to intercept all API calls and handle call rate limits"""

    MAX_RATE, MAX_PAUSE_INTERVAL = (95, pendulum.duration(minutes=10))
    MIN_RATE, MIN_PAUSE_INTERVAL = (85, pendulum.duration(minutes=2))
    MAX_SLEEP_TIME_FOR_RATE_LIMIT = 3600  # 1 hour
    current_sleep_time = 0
    SLEEP_TIME_EXCEEDED_MESSAGE = "Exceeded maximum sleep time waiting for rate limit to reset"

    @dataclass
    class Throttle:
        """Utilization of call rate in %, from 0 to 100"""

        per_application: float
        per_account: float

    # Insights async jobs throttle
    _ads_insights_throttle: Throttle
    _access_token = None
    _app_secret = None

    @property
    def ads_insights_throttle(self) -> Throttle:
        return self._ads_insights_throttle

    @staticmethod
    def _parse_call_rate_header(headers):
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
                usage = max(
                    usage,
                    usage_limits.get("call_count"),
                    usage_limits.get("total_cputime"),
                    usage_limits.get("total_time"),
                )
                pause_interval = max(
                    pause_interval,
                    pendulum.duration(minutes=usage_limits.get("estimated_time_to_regain_access", 0)),
                )

        return usage, pause_interval

    @classmethod
    def set_access_token(cls, access_token):
        cls._access_token = access_token

    @classmethod
    def set_app_secret(cls, app_secret):
        cls._app_secret = app_secret
    @classmethod
    def reset_session(cls):
        logger.info("resetting session after sleep")
        api = MyFacebookAdsApi.init(access_token=MyFacebookAdsApi._access_token, app_secret=MyFacebookAdsApi._app_secret, crash_log=False)
        FacebookAdsApi.set_default_api(api)

    def _compute_pause_interval(self, usage, pause_interval):
        """The sleep time will be calculated based on usage consumed."""
        if usage >= self.MAX_RATE:
            return max(self.MAX_PAUSE_INTERVAL, pause_interval)
        return max(self.MIN_PAUSE_INTERVAL, pause_interval)

    def _get_max_usage_pause_interval_from_batch(self, records):
        usage = 0
        pause_interval = self.MIN_PAUSE_INTERVAL

        for record in records:
            # there are two types of failures:
            # 1. no response (we execute batch until all inner requests has response)
            # 2. response with error (we crash loudly)
            # in case it is failed inner request the headers might not be present
            if "headers" not in record:
                continue
            headers = {header["name"].lower(): header["value"] for header in record["headers"]}
            usage_from_response, pause_interval_from_response = self._parse_call_rate_header(headers)
            usage = max(usage, usage_from_response)
            pause_interval = max(pause_interval_from_response, pause_interval)
        return usage, pause_interval

    def _handle_call_rate_limit(self, response, params):
        if "batch" in params:
            records = response.json()
            usage, pause_interval = self._get_max_usage_pause_interval_from_batch(records)
        else:
            headers = response.headers()
            usage, pause_interval = self._parse_call_rate_header(headers)

        if usage >= self.MIN_RATE:
            sleep_time = self._compute_pause_interval(usage=usage, pause_interval=pause_interval)
            logger.warning(f"Utilization is too high ({usage})%, pausing for {sleep_time}")
            sleep(sleep_time.total_seconds())
            self.current_sleep_time += sleep_time.total_seconds()
            if self.current_sleep_time >= self.MAX_SLEEP_TIME_FOR_RATE_LIMIT:
                raise AirbyteTracedException(self.SLEEP_TIME_EXCEEDED_MESSAGE, self.SLEEP_TIME_EXCEEDED_MESSAGE, FailureType.system_error)
            MyFacebookAdsApi.reset_session()

    def _update_insights_throttle_limit(self, response: FacebookResponse):
        """
        For /insights call every response contains x-fb-ads-insights-throttle
        header representing current throttle limit parameter for async insights
        jobs for current app/account.  We need this information to adjust
        number of running async jobs for optimal performance.
        """
        ads_insights_throttle = response.headers().get("x-fb-ads-insights-throttle")
        if ads_insights_throttle:
            ads_insights_throttle = json.loads(ads_insights_throttle)
            self._ads_insights_throttle = self.Throttle(
                per_application=ads_insights_throttle.get("app_id_util_pct", 0),
                per_account=ads_insights_throttle.get("acc_id_util_pct", 0),
            )

    @backoff_policy
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
        try:
            response = super().call(method, path, params, headers, files, url_override, api_version)
        except FacebookRequestError as exc:
            MyFacebookAdsApi.reset_session()
            raise exc
        except requests.exceptions.ConnectionError as exc:
            MyFacebookAdsApi.reset_session()
            body = {
                "error": {
                    "code": FACEBOOK_CONNECTION_RESET_ERROR_CODE,
                    "is_transient": "true",
                }
            }
            raise FacebookRequestError(str(exc), {}, 400, None, json.dumps(body))

        self._update_insights_throttle_limit(response)
        self._handle_call_rate_limit(response, params)
        return response


class API:
    """Simple wrapper around Facebook API"""

    def __init__(self, account_id: str, access_token: str, app_secret: str = None):
        self._account_id = account_id
        # design flaw in MyFacebookAdsApi requires such strange set of new default api instance
        self.api = MyFacebookAdsApi.init(access_token=access_token, app_secret=app_secret, crash_log=False)
        MyFacebookAdsApi.set_access_token(access_token)
        if app_secret:
            MyFacebookAdsApi.set_app_secret(app_secret=app_secret)
        FacebookAdsApi.set_default_api(self.api)

    @cached_property
    def account(self) -> AdAccount:
        """Find current account"""
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str) -> AdAccount:
        """Actual implementation of find account"""
        try:
            return AdAccount(f"act_{account_id}").api_get()
        except FacebookRequestError as exc:
            message = (
                f"Error: {exc.api_error_code()}, {exc.api_error_message()}. "
                f"Please also verify your Account ID: "
                f"See the https://www.facebook.com/business/help/1492627900875762 for more information."
            )
            raise AirbyteTracedException(
                message=message,
                failure_type=FailureType.config_error,
            ) from exc
