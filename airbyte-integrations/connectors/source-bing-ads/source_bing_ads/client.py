#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import os
import socket
import ssl
import sys
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Iterator, List, Mapping, Optional, Union
from urllib.error import URLError

import backoff
import pendulum
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from bingads.authorization import AuthorizationData, OAuthTokens, OAuthWebAuthCodeGrant
from bingads.exceptions import OAuthTokenRequestException
from bingads.service_client import ServiceClient
from bingads.util import errorcode_of_exception
from bingads.v13.bulk import BulkServiceManager, DownloadParameters
from bingads.v13.reporting.exceptions import ReportingDownloadException
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from suds import WebFault, sudsobject

FILE_TYPE = "Csv"
TIMEOUT_IN_MILLISECONDS = 3_600_000


class Client:
    api_version: int = 13
    refresh_token_safe_delta: int = 10  # in seconds
    logger: logging.Logger = logging.getLogger("airbyte")
    # retry on: rate limit errors, auth token expiration, internal errors
    # https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling
    # https://docs.microsoft.com/en-us/advertising/guides/operation-error-codes?view=bingads-13
    retry_on_codes: Iterator[str] = ["117", "207", "4204", "109", "0"]
    max_retries: int = 5
    # A backoff factor to apply between attempts after the second try
    # {retry_factor} * (2 ** ({number of total retries} - 1))
    retry_factor: int = 15
    # environments supported by Microsoft Advertising: sandbox, production
    environment: str = "production"
    # The time interval in milliseconds between two status polling attempts.
    report_poll_interval: int = 15000
    # Timeout of downloading report
    _download_timeout = 300000
    _max_download_timeout = 600000

    reports_start_date = None

    def __init__(
        self,
        tenant_id: str,
        reports_start_date: str = None,
        developer_token: str = None,
        client_id: str = None,
        client_secret: str = None,
        refresh_token: str = None,
        **kwargs: Mapping[str, Any],
    ) -> None:
        self.refresh_token = refresh_token
        self.developer_token = developer_token

        self.client_id = client_id
        self.client_secret = client_secret

        self.authentication = self._get_auth_client(client_id, tenant_id, client_secret)
        self.oauth: OAuthTokens = self._get_access_token()
        if reports_start_date:
            self.reports_start_date = pendulum.parse(reports_start_date).astimezone(tz=timezone.utc)

    def _get_auth_client(self, client_id: str, tenant_id: str, client_secret: str = None) -> OAuthWebAuthCodeGrant:
        # https://github.com/BingAds/BingAds-Python-SDK/blob/e7b5a618e87a43d0a5e2c79d9aa4626e208797bd/bingads/authorization.py#L390
        auth_creds = {
            "client_id": client_id,
            "redirection_uri": "",  # should be empty string
            "client_secret": None,
            "tenant": tenant_id,
        }
        # the `client_secret` should be provided for `non-public clients` only
        # https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13#request-accesstoken
        if client_secret and client_secret != "":
            auth_creds["client_secret"] = client_secret
        return OAuthWebAuthCodeGrant(**auth_creds)

    @lru_cache(maxsize=4)
    def _get_auth_data(self, customer_id: str = None, account_id: Optional[str] = None) -> AuthorizationData:
        return AuthorizationData(
            account_id=account_id,
            customer_id=customer_id,
            developer_token=self.developer_token,
            authentication=self.authentication,
        )

    def _get_access_token(self) -> OAuthTokens:
        self.logger.info("Fetching access token ...")
        # clear caches to be able to use new access token
        self.get_service.cache_clear()
        self._get_auth_data.cache_clear()
        try:
            tokens = self.authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)
        except OAuthTokenRequestException as e:
            raise AirbyteTracedException(
                message=str(e),
                internal_message="Failed to get OAuth access token by refresh token. "
                "The user could not be authenticated as the grant is expired. The user must sign in again.",
                failure_type=FailureType.config_error,
            )
        return tokens

    def is_token_expiring(self) -> bool:
        """
        Performs check if access token expiring in less than refresh_token_safe_delta seconds
        """
        token_total_lifetime: timedelta = datetime.utcnow() - self.oauth.access_token_received_datetime
        token_updated_expires_in: int = self.oauth.access_token_expires_in_seconds - token_total_lifetime.seconds
        return False if token_updated_expires_in > self.refresh_token_safe_delta else True

    def should_give_up(self, error: Union[WebFault, URLError, ReportingDownloadException]) -> bool:
        if isinstance(error, URLError):
            if (
                isinstance(error.reason, socket.timeout)
                or isinstance(error.reason, ssl.SSLError)
                or isinstance(error.reason, socket.gaierror)  # temporary failure in name resolution
            ):
                return False
        if isinstance(error, ReportingDownloadException):
            self.logger.info("Reporting file download tracking status timeout.")
            if self._download_timeout < self._max_download_timeout:
                self._download_timeout = self._download_timeout + 10000
                self.logger.info(f"Increasing time of timeout to {self._download_timeout}")
            return False

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
            (WebFault, URLError, ReportingDownloadException),
            max_tries=self.max_retries,
            factor=self.retry_factor,
            jitter=None,
            on_backoff=self.log_retry_attempt,
            giveup=self.should_give_up,
        )(self._request)(**kwargs)

    def _request(
        self,
        service_name: Optional[str],
        operation_name: str,
        customer_id: Optional[str],
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
            service = self._get_reporting_service(customer_id=customer_id, account_id=account_id)
        else:
            service = self.get_service(service_name=service_name, customer_id=customer_id, account_id=account_id)
        if operation_name == "download_report":
            params["download_parameters"].timeout_in_milliseconds = self._download_timeout
        return getattr(service, operation_name)(**params)

    @lru_cache(maxsize=4)
    def get_service(
        self,
        service_name: str,
        customer_id: str = None,
        account_id: Optional[str] = None,
    ) -> ServiceClient:
        return ServiceClient(
            service=service_name,
            version=self.api_version,
            authorization_data=self._get_auth_data(customer_id, account_id),
            environment=self.environment,
        )

    @lru_cache(maxsize=4)
    def _get_reporting_service(
        self,
        customer_id: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> ServiceClient:
        return ReportingServiceManager(
            authorization_data=self._get_auth_data(customer_id, account_id),
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

    def _bulk_service_manager(self, customer_id: Optional[str] = None, account_id: Optional[str] = None):
        return BulkServiceManager(
            authorization_data=self._get_auth_data(customer_id, account_id),
            poll_interval_in_milliseconds=5000,
            environment=self.environment,
        )

    def get_bulk_entity(
        self,
        download_entities: List[str],
        data_scope: List[str],
        customer_id: Optional[str] = None,
        account_id: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> str:
        """
        Return path with zipped csv archive
        """
        download_parameters = DownloadParameters(
            # campaign_ids=None,
            data_scope=data_scope,
            download_entities=download_entities,
            file_type=FILE_TYPE,
            last_sync_time_in_utc=start_date,
            result_file_directory=os.getcwd(),
            result_file_name=str(uuid.uuid4()),
            overwrite_result_file=True,  # Set this value true if you want to overwrite the same file.
            timeout_in_milliseconds=TIMEOUT_IN_MILLISECONDS,  # You may optionally cancel the download after a specified time interval.
        )
        bulk_service_manager = self._bulk_service_manager(customer_id=customer_id, account_id=account_id)
        return bulk_service_manager.download_file(download_parameters)
