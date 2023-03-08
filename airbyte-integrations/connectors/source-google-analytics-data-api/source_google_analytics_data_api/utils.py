#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import calendar
import datetime
from functools import wraps
from typing import Any, Dict, Iterable, Mapping, Optional

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams.http import auth
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator

DATE_FORMAT = "%Y-%m-%d"

metrics_data_native_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": str,
    "TYPE_INTEGER": int,
    "TYPE_FLOAT": float,
    "TYPE_SECONDS": float,
    "TYPE_MILLISECONDS": float,
    "TYPE_MINUTES": float,
    "TYPE_HOURS": float,
    "TYPE_STANDARD": float,
    "TYPE_CURRENCY": float,
    "TYPE_FEET": float,
    "TYPE_MILES": float,
    "TYPE_METERS": float,
    "TYPE_KILOMETERS": float,
}

metrics_data_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": "string",
    "TYPE_INTEGER": "integer",
    "TYPE_FLOAT": "number",
    "TYPE_SECONDS": "number",
    "TYPE_MILLISECONDS": "number",
    "TYPE_MINUTES": "number",
    "TYPE_HOURS": "number",
    "TYPE_STANDARD": "number",
    "TYPE_CURRENCY": "number",
    "TYPE_FEET": "number",
    "TYPE_MILES": "number",
    "TYPE_METERS": "number",
    "TYPE_KILOMETERS": "number",
}

authenticator_class_map: Dict = {
    "Service": (GoogleServiceKeyAuthenticator, lambda credentials: {"credentials": credentials["credentials_json"]}),
    "Client": (
        auth.Oauth2Authenticator,
        lambda credentials: {
            "token_refresh_endpoint": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "client_secret": credentials["client_secret"],
            "client_id": credentials["client_id"],
            "refresh_token": credentials["refresh_token"],
        },
    ),
}


def datetime_to_secs(dt: datetime.datetime) -> int:
    return calendar.timegm(dt.utctimetuple())


def string_to_date(d: str, f: str = DATE_FORMAT, old_format=None) -> datetime.date:
    # To convert the old STATE date format "YYYY-MM-DD" to the new format "YYYYMMDD" we need this `old_format` additional param.
    # As soon as all current cloud sync will be converted to the new format we can remove this double format support.
    if old_format:
        try:
            return datetime.datetime.strptime(d, old_format).date()
        except ValueError:
            pass
    return datetime.datetime.strptime(d, f).date()


def date_to_string(d: datetime.date, f: str = DATE_FORMAT) -> str:
    return d.strftime(f)


def get_metrics_type(t: str) -> str:
    return metrics_data_types_map.get(t, "number")


def metrics_type_to_python(t: str) -> type:
    return metrics_data_native_types_map.get(t, str)


def get_dimensions_type(d: str) -> str:
    return "string"


class GoogleAnalyticsApiQuota:

    # Airbyte Logger
    logger = AirbyteLogger()
    # initial quota placeholder
    initial_quota: Optional[Mapping[str, Any]] = None
    # the % value cutoff, crossing which will trigger
    # setting the scenario values for attrs prior to the 429 error
    treshold: float = 0.1
    # base attrs
    should_retry: Optional[bool] = True
    backoff_time: Optional[int] = None
    raise_on_http_errors: bool = True
    # stop making new slices globaly
    stop_iter: bool = False
    # mapping with scenarios for each quota kind
    quota_mapping: Mapping[str, Any] = {
        "concurrentRequests": {
            "error_pattern": "Exhausted concurrent requests quota.",
            "backoff": 30,
            "should_retry": True,
            "raise_on_http_errors": False,
            "stop_iter": False,
        },
        "tokensPerProjectPerHour": {
            "error_pattern": "Exhausted property tokens for a project per hour.",
            "backoff": 1800,
            "should_retry": True,
            "raise_on_http_errors": False,
            "stop_iter": False,
        },
        # 'tokensPerDay': {
        #     'error_pattern': "___",
        #     "backoff": None,
        #     "should_retry": False,
        #     "raise_on_http_errors": False,
        #     "stop_iter": True,
        # },
        # 'tokensPerHour': {
        #     'error_pattern': "___",
        #     "backoff": 1800,
        #     "should_retry": True,
        #     "raise_on_http_errors": False,
        #     "stop_iter": False,
        # },
        # 'serverErrorsPerProjectPerHour': {
        #     'error_pattern': "___",
        #     "backoff": 3600,
        #     "should_retry": True,
        #     "raise_on_http_errors": False,
        #     "stop_iter": False,
        # },
        # 'potentiallyThresholdedRequestsPerHour': {
        #     'error_pattern': "___",
        #     "backoff": 1800,
        #     "should_retry": True,
        #     "raise_on_http_errors": False,
        #     "stop_iter": False,
        # },
    }

    def _get_known_quota_list(self) -> Iterable[str]:
        return self.quota_mapping.keys()

    def _get_initial_quota_value(self, quota_name: str) -> int:
        init_remaining = self.initial_quota.get(quota_name).get("remaining")
        # before the 429 is hit the `remaining` could become -1 or 0
        return 1 if init_remaining <= 0 else init_remaining

    def _get_quota_name_from_error_message(self, error_msg: str) -> Optional[str]:
        for quota, value in self.quota_mapping.items():
            if value.get("error_pattern") in error_msg:
                return quota
        return None

    def _get_known_quota_from_current(self, property_quota: Mapping[str, Any]) -> Mapping[str, Any]:
        current_quota = {}
        for quota in property_quota.keys():
            if quota in self._get_known_quota_list():
                current_quota.update(**{quota: property_quota.get(quota)})
        return current_quota

    def _set_attrs_values_for_quota(self, quota_name: str) -> None:
        quota = self.quota_mapping.get(quota_name, {})
        if quota:
            self.should_retry = quota.get("should_retry")
            self.raise_on_http_errors = quota.get("raise_on_http_errors")
            self.stop_iter = quota.get("stop_iter")
            self.backoff_time = quota.get("backoff")

    def _set_default_attrs(self) -> None:
        self.should_retry = True
        self.backoff_time = None
        self.raise_on_http_errors = True
        self.stop_iter = False

    def _set_initial_quota(self, current_quota: Optional[Mapping[str, Any]] = None) -> None:
        if not self.initial_quota:
            self.initial_quota = current_quota

    def _check_remaining(self, current_quota: Mapping[str, Any]) -> None:
        for quota_name, quota_value in current_quota.items():
            total_available = self._get_initial_quota_value(quota_name)
            remaining: int = quota_value.get("remaining")
            remaining_percent: float = remaining / total_available
            # make an early stop if we faced with the quota that is going to run out
            if remaining_percent <= self.treshold:
                self.logger.warn(f"The `{quota_name}` quota is running out of tokens. Available {remaining} out of {total_available}.")
                self._set_attrs_values_for_quota(quota_name)
                return None

    def _check_for_errors(self, response: requests.Response) -> None:
        try:
            # revert to default values after successul retry
            self._set_default_attrs()
            error = response.json().get("error")
            print(f"\nERROR_check_for_errors: {error, response.json()}\n")
            if error:
                quota_name = self._get_quota_name_from_error_message(error.get("message"))
                if quota_name:
                    print(f"\nAFTER_check_for_errors: {quota_name}\n")
                    self._set_attrs_values_for_quota(quota_name)
                    self.logger.warn(f"The `{quota_name}` quota is exceeded!")
                    return None
        except Exception as e:
            self.logger.fatal(f"Other `GoogleAnalyticsApiQuota` error: {e}")
            raise

    def check_quota(self) -> None:
        """
        RESPONSE EXAMPLE:
            'propertyQuota': {
                'tokensPerDay': {
                    'consumed': 1,
                    'remaining': 23155
                },
                'tokensPerHour': {
                    'consumed': 1,
                    'remaining': 4985
                },
                'concurrentRequests': {
                    'consumed': 0,
                    'remaining': 10
                },
                'serverErrorsPerProjectPerHour': {
                    'consumed': 0,
                    'remaining': 10
                },
                'potentiallyThresholdedRequestsPerHour': {
                    'consumed': 0,
                    'remaining': 120
                },
                'tokensPerProjectPerHour': {
                    'consumed': 1,
                    'remaining': 1735
                }
            }
        """

        def decorator(func):
            @wraps(func)
            def wrapper_check_quota(*args, **kwargs):
                response = args[1]
                # get current quota
                property_quota: dict = response.json().get("propertyQuota")
                if property_quota:
                    # return default attrs values once successfully retried
                    # or untill another 429 error is hit
                    self._set_default_attrs()
                    # reduce quota list to known kinds only
                    current_quota = self._get_known_quota_from_current(property_quota)
                    if current_quota:
                        # save the initial quota
                        self._set_initial_quota(current_quota)
                        # check for remaining quota
                        self._check_remaining(current_quota)
                else:
                    self._check_for_errors(response)
                return func(*args, **kwargs)

            return wrapper_check_quota

        return decorator
