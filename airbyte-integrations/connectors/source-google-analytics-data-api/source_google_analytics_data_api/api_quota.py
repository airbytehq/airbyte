#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from functools import wraps
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from requests.exceptions import JSONDecodeError

from .utils import API_LIMIT_PER_HOUR


class GoogleAnalyticsApiQuotaBase:
    # Airbyte Logger
    logger = logging.getLogger("airbyte")
    # initial quota placeholder
    initial_quota: Optional[Mapping[str, Any]] = None
    # the % value cutoff, crossing which will trigger
    # setting the scenario values for attrs prior to the 429 error
    treshold: float = 0.1
    # base attrs
    response_action: ResponseAction = ResponseAction.RETRY
    backoff_time: Optional[int] = None
    # stop making new slices globally
    stop_iter: bool = False
    error_message = None
    # mapping with scenarios for each quota kind
    quota_mapping: Mapping[str, Any] = {
        "concurrentRequests": {
            "error_pattern": "Exhausted concurrent requests quota.",
            "backoff": 30,
            "response_action": ResponseAction.RETRY,
            "stop_iter": False,
        },
        "tokensPerProjectPerHour": {
            "error_pattern": "Exhausted property tokens for a project per hour.",
            "backoff": 1800,
            "response_action": ResponseAction.RETRY,
            "stop_iter": False,
            "error_message": API_LIMIT_PER_HOUR,
        },
        "potentiallyThresholdedRequestsPerHour": {
            "error_pattern": "Exhausted potentially thresholded requests quota.",
            "backoff": 1800,
            "response_action": ResponseAction.RETRY,
            "stop_iter": False,
            "error_message": API_LIMIT_PER_HOUR,
        },
        # TODO: The next scenarios are commented out for now.
        # When we face with one of these at least 1 time,
        # we should be able to uncomment the one matches the criteria
        # and fill-in the `error_pattern` to track that quota as well.
        # IMPORTANT: PLEASE DO NOT REMOVE the scenario down bellow!
        # 'tokensPerDay': {
        #     'error_pattern': "___",
        #     "backoff": None,
        #     "response_action": ResponseAction.FAIL,
        #     "stop_iter": True,
        # },
        # 'tokensPerHour': {
        #     'error_pattern': "___",
        #     "backoff": 1800,
        #     "response_action": ResponseAction.RETRY,
        #     "stop_iter": False,
        # },
        # 'serverErrorsPerProjectPerHour': {
        #     'error_pattern': "___",
        #     "backoff": 3600,
        #     "response_action": ResponseAction.RETRY,
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

    def _get_known_quota_from_response(self, property_quota: Mapping[str, Any]) -> Mapping[str, Any]:
        current_quota = {}
        for quota in property_quota.keys():
            if quota in self._get_known_quota_list():
                current_quota.update(**{quota: property_quota.get(quota)})
        return current_quota

    def _set_retry_attrs_for_quota(self, quota_name: str) -> None:
        quota = self.quota_mapping.get(quota_name, {})
        if quota:
            self.response_action = quota.get("response_action")
            self.stop_iter = quota.get("stop_iter")
            self.backoff_time = quota.get("backoff")
            self.error_message = quota.get("error_message", quota.get("error_pattern"))

    def _set_default_handle_error_attrs(self) -> None:
        self.response_action = ResponseAction.RETRY
        self.backoff_time = None
        self.stop_iter = False

    def _set_initial_quota(self, current_quota: Optional[Mapping[str, Any]] = None) -> None:
        if not self.initial_quota:
            self.initial_quota = current_quota

    def _check_remaining_quota(self, current_quota: Mapping[str, Any]) -> None:
        for quota_name, quota_value in current_quota.items():
            total_available = self._get_initial_quota_value(quota_name)
            remaining: int = quota_value.get("remaining")
            remaining_percent: float = remaining / total_available
            # make an early stop if we faced with the quota that is going to run out
            if remaining_percent <= self.treshold:
                self.logger.warning(f"The `{quota_name}` quota is running out of tokens. Available {remaining} out of {total_available}.")
                self._set_retry_attrs_for_quota(quota_name)
                return None
            elif self.error_message:
                self.logger.warning(self.error_message)

    def _check_for_errors(self, response: requests.Response) -> None:
        try:
            # revert to default values after successul retry
            self._set_default_handle_error_attrs()
            error = response.json().get("error")
            if error:
                quota_name = self._get_quota_name_from_error_message(error.get("message"))
                if quota_name:
                    self._set_retry_attrs_for_quota(quota_name)
                    self.logger.warn(f"The `{quota_name}` quota is exceeded!")
                    return None
        except (AttributeError, JSONDecodeError) as attr_e:
            self.logger.warning(
                f"`GoogleAnalyticsApiQuota._check_for_errors`: Received non JSON response from the API. Full error: {attr_e}. Bypassing."
            )
            pass
        except Exception as e:
            self.logger.fatal(f"Other `GoogleAnalyticsApiQuota` error: {e}")
            raise


class GoogleAnalyticsApiQuota(GoogleAnalyticsApiQuotaBase):
    def _check_quota(self, response: requests.Response):
        # try get json from response
        try:
            parsed_response = response.json()
        except (AttributeError, JSONDecodeError) as e:
            self.logger.warning(
                f"`GoogleAnalyticsApiQuota._check_quota`: Received non JSON response from the API. Full error: {e}. Bypassing."
            )
            parsed_response = {}
        # get current quota
        property_quota: dict = parsed_response.get("propertyQuota")
        if property_quota:
            # return default attrs values once successfully retried
            # or until another 429 error is hit
            self._set_default_handle_error_attrs()
            # reduce quota list to known kinds only
            current_quota = self._get_known_quota_from_response(property_quota)
            if current_quota:
                # save the initial quota
                self._set_initial_quota(current_quota)
                # check for remaining quota
                self._check_remaining_quota(current_quota)
        else:
            self._check_for_errors(response)

    def handle_quota(self) -> None:
        """
        The function decorator is used to integrate with the `interpret_response` method,
        or any other method that provides early access to the `response` object.
        """

        def decorator(func):
            @wraps(func)
            def wrapper_handle_quota(*args, **kwargs):
                # find the requests.Response inside args list
                for arg in args:
                    response = arg if isinstance(arg, requests.models.Response) else None
                # check for the quota
                self._check_quota(response)
                # return actual function
                return func(*args, **kwargs)

            return wrapper_handle_quota

        return decorator
