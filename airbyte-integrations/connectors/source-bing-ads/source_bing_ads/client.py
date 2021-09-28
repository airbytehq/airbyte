#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import sys
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Iterator, Mapping, Optional

import backoff
import pendulum
from airbyte_cdk.logger import AirbyteLogger
from bingads.authorization import AuthorizationData, OAuthTokens, OAuthWebAuthCodeGrant
from bingads.service_client import ServiceClient
from bingads.util import errorcode_of_exception
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from suds import WebFault, sudsobject


class Client:
    api_version: int = 13
    refresh_token_safe_delta: int = 10  # in seconds
    logger: AirbyteLogger = AirbyteLogger()
    # retry on: rate limit errors, auth token expiration, internal errors
    # https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling
    # https://docs.microsoft.com/en-us/advertising/guides/operation-error-codes?view=bingads-13
    retry_on_codes: Iterator[str] = ["117", "207", "4204", "109", "0"]
    max_retries: int = 3
    # A backoff factor to apply between attempts after the second try
    # {retry_factor} * (2 ** ({number of total retries} - 1))
    retry_factor: int = 15
    # environments supported by Microsoft Advertising: sandbox, production
    environment: str = "production"
    # The time interval in milliseconds between two status polling attempts.
    report_poll_interval: int = 15000

    def __init__(
        self,
        developer_token: str,
        customer_id: str,
        client_secret: str,
        client_id: str,
        refresh_token: str,
        reports_start_date: str,
        hourly_reports: bool,
        daily_reports: bool,
        weekly_reports: bool,
        monthly_reports: bool,
        **kwargs: Mapping[str, Any],
    ) -> None:
        self.authorization_data: Mapping[str, AuthorizationData] = {}
        self.authentication = OAuthWebAuthCodeGrant(
            client_id,
            client_secret,
            "",
        )

        self.refresh_token = refresh_token
        self.customer_id = customer_id
        self.developer_token = developer_token
        self.hourly_reports = hourly_reports
        self.daily_reports = daily_reports
        self.weekly_reports = weekly_reports
        self.monthly_reports = monthly_reports

        self.oauth: OAuthTokens = self._get_access_token()
        self.reports_start_date = pendulum.parse(reports_start_date).astimezone(tz=timezone.utc)

    @lru_cache(maxsize=None)
    def _get_auth_data(self, account_id: Optional[str] = None) -> AuthorizationData:
        return AuthorizationData(
            account_id=account_id,
            customer_id=self.customer_id,
            developer_token=self.developer_token,
            authentication=self.authentication,
        )

    def _get_access_token(self) -> OAuthTokens:
        self.logger.info("Fetching access token ...")
        # clear caches to be able to use new access token
        self.get_service.cache_clear()
        self._get_auth_data.cache_clear()
        return self.authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)

    def is_token_expiring(self) -> bool:
        """
        Performs check if access token expiring in less than refresh_token_safe_delta seconds
        """
        token_total_lifetime: timedelta = datetime.utcnow() - self.oauth.access_token_received_datetime
        token_updated_expires_in: int = self.oauth.access_token_expires_in_seconds - token_total_lifetime.seconds
        return False if token_updated_expires_in > self.refresh_token_safe_delta else True

    def should_retry(self, error: WebFault) -> bool:
        error_code = str(errorcode_of_exception(error))
        give_up = error_code not in self.retry_on_codes
        if give_up:
            self.logger.error(f"Giving up for returned error code: {error_code}. Error details: {self._get_error_message(error)}")
        return give_up

    def _get_error_message(self, error: WebFault) -> str:
        return str(self.asdict(error.fault)) if hasattr(error, "fault") else str(error)

    def log_retry_attempt(self, details: Mapping[str, Any]) -> None:
        _, exc, _ = sys.exc_info()
        self.logger.info(
            f"Caught retryable error: {self._get_error_message(exc)} after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        )

    def request(self, **kwargs: Mapping[str, Any]) -> Mapping[str, Any]:
        return backoff.on_exception(
            backoff.expo,
            WebFault,
            max_tries=self.max_retries,
            factor=self.retry_factor,
            jitter=None,
            on_backoff=self.log_retry_attempt,
            giveup=self.should_retry,
        )(self._request)(**kwargs)

    def _request(
        self,
        service_name: Optional[str],
        operation_name: str,
        account_id: Optional[str],
        params: Mapping[str, Any],
        is_report_service: bool = False,
    ) -> Mapping[str, Any]:
        """
        Executes appropriate Service Operation on Bing Ads API
        """
        if self.is_token_expiring():
            self.oauth = self._get_access_token()

        if is_report_service:
            service = self._get_reporting_service(account_id=account_id)
        else:
            service = self.get_service(service_name=service_name, account_id=account_id)

        return getattr(service, operation_name)(**params)

    @lru_cache(maxsize=None)
    def get_service(
        self,
        service_name: str,
        account_id: Optional[str] = None,
    ) -> ServiceClient:
        return ServiceClient(
            service=service_name,
            version=self.api_version,
            authorization_data=self._get_auth_data(account_id),
            environment=self.environment,
        )

    @lru_cache(maxsize=None)
    def _get_reporting_service(
        self,
        account_id: Optional[str] = None,
    ) -> ServiceClient:
        return ReportingServiceManager(
            authorization_data=self._get_auth_data(account_id),
            poll_interval_in_milliseconds=self.report_poll_interval,
            environment=self.environment,
        )

    @classmethod
    def asdict(cls, suds_object: sudsobject.Object) -> Mapping[str, Any]:
        """
        Converts nested Suds Object into serializable format.
        Input sample:
        {
            obj[] =
                {
                    value = 1
                },
                {
                    value = "str"
                },
        }
        Output sample: =>
        {'obj': [{'value': 1}, {'value': 'str'}]}
        """
        result: Mapping[str, Any] = {}

        for field, val in sudsobject.asdict(suds_object).items():
            if hasattr(val, "__keylist__"):
                result[field] = cls.asdict(val)
            elif isinstance(val, list):
                result[field] = []
                for item in val:
                    if hasattr(item, "__keylist__"):
                        result[field].append(cls.asdict(item))
                    else:
                        result[field].append(item)
            elif isinstance(val, datetime):
                result[field] = val.isoformat()
            else:
                result[field] = val
        return result
