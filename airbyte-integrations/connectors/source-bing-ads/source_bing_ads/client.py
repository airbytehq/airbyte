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

import sys
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Iterator, Mapping, Optional

import backoff
from airbyte_cdk.logger import AirbyteLogger
from bingads.authorization import AuthorizationData, OAuthTokens, OAuthWebAuthCodeGrant
from bingads.service_client import ServiceClient
from bingads.util import errorcode_of_exception
from suds import WebFault, sudsobject


class Client:
    api_version: int = 13
    refresh_token_safe_delta: int = 10  # in seconds
    logger: AirbyteLogger = AirbyteLogger()
    # retry on rate limit errors , when auth token expired or on some internal errors
    # https://docs.microsoft.com/en-us/advertising/guides/services-protocol?view=bingads-13#throttling
    # https://docs.microsoft.com/en-us/advertising/guides/operation-error-codes?view=bingads-13
    retry_on_codes: Iterator[int] = [117, 207, 4204, 109, 0]
    max_retries: int = 3
    retry_factor: int = 15

    def __init__(
        self,
        developer_token: str,
        account_ids: Iterator[str],
        customer_id: str,
        client_secret: str,
        client_id: str,
        refresh_token: str,
        **kwargs: Mapping[str, Any],
    ) -> None:

        if not account_ids:
            raise Exception("At least one id in account_ids is required.")

        self.authorization_data: Mapping[str, AuthorizationData] = {}
        self.authentication = OAuthWebAuthCodeGrant(
            client_id,
            client_secret,
            "",
        )

        self.refresh_token = refresh_token
        self.account_ids = account_ids

        self.oauth: OAuthTokens = self._get_access_token()
        # self.authentication.oauth_tokens.access_token = self.authentication.oauth_tokens.access_token + 'asfas'
        for account_id in account_ids:
            self.authorization_data[account_id] = AuthorizationData(
                account_id=account_id,
                customer_id=customer_id,
                developer_token=developer_token,
                authentication=self.authentication,
            )

        # setup default authorization data for requests which don't depend on concrete account id
        self.authorization_data[None] = self.authorization_data[account_ids[0]]

    def _get_access_token(self) -> OAuthTokens:
        self.logger.info("Fetching access token ...")
        # clear caches to be able to use new access token
        self.get_service.cache_clear()
        return self.authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)

    def is_token_expiring(self) -> bool:
        """
        Performs check if access token expiring in less than refresh_token_safe_delta seconds
        """
        token_total_lifetime: timedelta = datetime.utcnow() - self.oauth.access_token_received_datetime
        token_updated_expires_in: int = self.oauth.access_token_expires_in_seconds - token_total_lifetime.seconds
        return False if token_updated_expires_in > self.refresh_token_safe_delta else True

    def should_retry(self, error: WebFault) -> bool:
        error_code = errorcode_of_exception(error)
        give_up = error_code in self.retry_on_codes
        if give_up:
            self.logger.info(f"Giving up for returned error code: {error_code}")
        return give_up

    def log_retry_attempt(self, details):
        _, exc, _ = sys.exc_info()
        error = self.asdict(exc.fault) if hasattr(exc, "fault") else exc

        self.logger.info(str(error))
        self.logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")

    def request(self, **kwargs):
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
        service_name: str,
        operation_name: str,
        account_id: Optional[str],
        params: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Executes appropriate Service Operation on Bing Ads API
        """
        if self.is_token_expiring():
            self.oauth = self._get_access_token()

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
            authorization_data=self.authorization_data[account_id],
            # environments supported by Microsoft Advertising: sandbox, production
            environment="production",
        )

    @classmethod
    def asdict(cls, suds_object: sudsobject.Object) -> Mapping[str, Any]:
        """
        Converts nested Suds Object into serializable format.
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
