#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import csv
import gzip
import json
import logging
import threading
import time
from dataclasses import InitVar, dataclass
from datetime import datetime as dt
from io import StringIO
from typing import Any, Callable, Dict, Generator, List, Mapping, MutableMapping, Optional, Tuple, Union

import backoff
import dateparser
import requests
import xmltodict

from airbyte_cdk import InterpolatedString
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.validators.validation_strategy import ValidationStrategy
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


logger = logging.getLogger("airbyte")

# Module-level references to authenticator instances for token invalidation on 403 errors
_authenticator_instances: List["AmazonSPOauthAuthenticator"] = []

# Expiry threshold for Restricted Data Tokens (in seconds). RDTs are valid for 1 hour;
# we refresh proactively at 50 minutes to avoid using an expired token.
_RDT_REFRESH_THRESHOLD_SECONDS = 50 * 60

# Error message that indicates the access token has expired (returned by Amazon SP API)
TOKEN_EXPIRED_ERROR_MESSAGE = "The access token you provided has expired."


@dataclass
class AmazonSPOauthAuthenticator(DeclarativeOauth2Authenticator):
    """
    This class extends the DeclarativeOauth2Authenticator functionality
    and allows to pass custom headers to the refresh access token requests.

    It also supports reactive token refresh when the Amazon SP API returns a 403 error
    indicating the access token has expired.
    """

    host: Union[InterpolatedString, str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._host = InterpolatedString.create(self.host, parameters=parameters)
        # Register this instance for token invalidation by the backoff strategy
        global _authenticator_instances
        _authenticator_instances.append(self)

    def get_auth_header(self) -> Mapping[str, Any]:
        return {
            "host": self._host.eval(self.config),
            "user-agent": "python-requests",
            "x-amz-access-token": self.get_access_token(),
            "x-amz-date": ab_datetime_now().strftime("%Y%m%dT%H%M%SZ"),
        }

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        return {"Content-Type": "application/x-www-form-urlencoded"}

    def invalidate_token(self) -> None:
        """
        Force the token to appear expired so that the next call to get_access_token()
        will trigger a refresh. This is called when the Amazon SP API returns a 403 error
        with a message indicating the access token has expired.
        """
        # Set the token expiry date to the past to force a refresh
        self.set_token_expiry_date(ab_datetime_parse("1970-01-01T00:00:00Z"))
        logger.info("Access token invalidated due to 403 'token expired' response from Amazon SP API")


@dataclass
class AmazonSPRdtAuthenticator(AmazonSPOauthAuthenticator):
    """
    Extends AmazonSPOauthAuthenticator to support Restricted Data Tokens (RDT) for
    accessing PII fields (BuyerInfo, ShippingAddress) on Orders-related endpoints.

    When the ``include_pii`` config flag is ``True``, this authenticator:
      1. Requests an RDT scoped to the configured ``restricted_resource_paths``.
      2. Caches the RDT and proactively refreshes it before the 50-minute threshold.
      3. Falls back to the standard LWA token on HTTP 403 (missing Restricted Role).
      4. Raises a config error for any other RDT request failure.
    """

    restricted_resource_paths: Optional[List[str]] = None
    _RDT_API_VERSION: str = "2021-03-01"
    _rdt_lock: threading.Lock = threading.Lock()

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._rdt_token: Optional[str] = None
        self._rdt_fetch_time: Optional[float] = None
        self._rdt_fallback_to_lwa: bool = False

    def get_auth_header(self) -> Mapping[str, Any]:
        include_pii = self.config.get("include_pii", False)

        if include_pii and not self._rdt_fallback_to_lwa:
            rdt_token = self._get_rdt_token()
            if rdt_token:
                return {
                    "host": self._host.eval(self.config),
                    "user-agent": "python-requests",
                    "x-amz-access-token": rdt_token,
                    "x-amz-date": ab_datetime_now().strftime("%Y%m%dT%H%M%SZ"),
                }

        # Fall back to standard LWA token (non-PII mode)
        return super().get_auth_header()

    # ------------------------------------------------------------------
    # RDT lifecycle helpers
    # ------------------------------------------------------------------

    def _get_rdt_token(self) -> Optional[str]:
        """Return a cached RDT if still fresh, otherwise fetch a new one.

        Uses double-checked locking to prevent multiple threads from
        refreshing the token simultaneously (see airbyte-python-cdk#883).
        """
        current_time = time.monotonic()
        if self._rdt_token and self._rdt_fetch_time is not None:
            if current_time - self._rdt_fetch_time <= _RDT_REFRESH_THRESHOLD_SECONDS:
                return self._rdt_token

        with self._rdt_lock:
            # Re-check after acquiring the lock; another thread may have refreshed already.
            current_time = time.monotonic()
            if self._rdt_token and self._rdt_fetch_time is not None:
                if current_time - self._rdt_fetch_time <= _RDT_REFRESH_THRESHOLD_SECONDS:
                    return self._rdt_token
            return self._fetch_rdt_token()

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"RDT request: retryable error after {details['tries']} tries. Waiting {details['wait']:.1f}s then retrying..."
        ),
        max_time=300,
    )
    def _fetch_rdt_token(self) -> Optional[str]:
        """Request a new RDT from the Amazon Tokens API."""

        endpoint = self.config.get("endpoint", "")
        tokens_url = f"{endpoint}/tokens/{self._RDT_API_VERSION}/restrictedDataToken"

        restricted_resources = [
            {
                "method": "GET",
                "path": path,
                "dataElements": ["buyerInfo", "shippingAddress"],
            }
            for path in self.restricted_resource_paths or []
        ]

        lwa_token = self.get_access_token()
        headers = {
            "content-type": "application/json",
            "x-amz-access-token": lwa_token,
            "x-amz-date": ab_datetime_now().strftime("%Y%m%dT%H%M%SZ"),
            "host": self._host.eval(self.config),
            "user-agent": "python-requests",
        }

        try:
            response = requests.post(
                tokens_url,
                json={"restrictedResources": restricted_resources},
                headers=headers,
            )

            if response.status_code == 403:
                logger.warning("RDT request returned HTTP 403 (PII access is not available). Falling back to standard LWA token.")
                self._rdt_fallback_to_lwa = True
                return None

            if not response.ok:
                response.raise_for_status()

            data = response.json()
            self._rdt_token = data["restrictedDataToken"]
            add_to_secrets(self._rdt_token)
            self._rdt_fetch_time = time.monotonic()
            logger.info("Successfully obtained a RDT for PII access.")
            return self._rdt_token

        except requests.exceptions.RequestException as exc:
            if exc.response is not None and (exc.response.status_code == 429 or exc.response.status_code >= 500):
                raise DefaultBackoffException(
                    request=exc.response.request,
                    response=exc.response,
                    failure_type=FailureType.transient_error,
                )
            raise AirbyteTracedException(
                message=(f"Failed to request a RDT from Amazon SP-API: {exc}."),
                failure_type=FailureType.config_error,
            ) from exc


@dataclass
class AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy(WaitTimeFromHeaderBackoffStrategy):
    """
    This strategy is designed for scenarios where the server communicates retry-after durations
    through HTTP headers. The wait time is derived by taking the reciprocal of the value extracted
    from the header. If the header does not provide a valid time, a default backoff time is used.

    Additionally, this strategy detects when the Amazon SP API returns a 403 error with a message
    indicating the access token has expired, and invalidates the token so that the next retry
    will use a fresh token.
    """

    default_backoff_time: Optional[float] = 10

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        # Check if this is a token expiration error and invalidate the token if so
        self._check_and_invalidate_expired_token(response_or_exception)

        time_from_header = super().backoff_time(response_or_exception, attempt_count)
        if time_from_header:
            return 1 / float(time_from_header)
        else:
            return self.default_backoff_time

    @staticmethod
    def _check_and_invalidate_expired_token(
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
    ) -> None:
        """
        Check if the response contains the specific "access token expired" error message
        from Amazon SP API and invalidate the token if so.

        The error message can appear in either the 'message' or 'details' field of the
        error response, so we check both fields.
        """
        if not isinstance(response_or_exception, requests.Response):
            return

        if response_or_exception.status_code != 403:
            return

        try:
            response_json = response_or_exception.json()
            errors = response_json.get("errors", [])
            for error in errors:
                # Check both 'message' and 'details' fields as Amazon SP API may return
                # the token expiration error in either field
                message = error.get("message", "")
                details = error.get("details", "")
                if TOKEN_EXPIRED_ERROR_MESSAGE in message or TOKEN_EXPIRED_ERROR_MESSAGE in details:
                    for instance in _authenticator_instances:
                        instance.invalidate_token()
                    return
        except (json.JSONDecodeError, AttributeError, TypeError):
            # If we can't parse the response, don't invalidate
            pass


@dataclass
class GzipCsvDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        yield from csv.DictReader(StringIO(document), delimiter="\t")


@dataclass
class GzipXmlDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            parsed = xmltodict.parse(document, attr_prefix="", cdata_key="value", force_list={"Message"})
        except Exception as e:
            logger.warning(f"Unable to parse the report for the stream, error: {str(e)}")
            raise

        reports = parsed.get("AmazonEnvelope", {}).get("Message", {})
        for report in reports:
            yield report.get("OrderReport", {})


@dataclass
class GzipJsonDecoder(Decoder):
    """
    Decoder strategy that attempts to decompress a response using GZIP first and then parses the resulting
    document as JSON. Also as a backup, this works for uncompressed responses that are already in JSON format
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            body_json = json.loads(document)
            yield from self.parse_body_json(body_json)
        except requests.exceptions.JSONDecodeError:
            logger.warning(f"Response cannot be parsed into json: {response.status_code=}, {response.text=}")
            yield {}

    @staticmethod
    def parse_body_json(
        body_json: MutableMapping[str, Any] | List[MutableMapping[str, Any]],
    ) -> Generator[MutableMapping[str, Any], None, None]:
        if not isinstance(body_json, list):
            body_json = [body_json]
        if len(body_json) == 0:
            yield {}
        else:
            yield from body_json


@dataclass
class SellerFeedbackReportsGzipCsvDecoder(Decoder):
    parameters: InitVar[Mapping[str, Any]]
    NORMALIZED_FIELD_NAMES = ["date", "rating", "comments", "response", "order_id", "rater_email"]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        # csv header field names for this report differ per marketplace (are localized to marketplace language)
        # but columns come in the same order, so we set fieldnames to our custom ones
        # and raise error if original and custom header field count does not match
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        reader = csv.DictReader(StringIO(document), delimiter="\t", fieldnames=self.NORMALIZED_FIELD_NAMES)
        original_fieldnames = next(reader)
        if len(original_fieldnames) != len(self.NORMALIZED_FIELD_NAMES):
            raise ValueError("Original and normalized header field count does not match")

        yield from reader


@dataclass
class GetXmlBrowseTreeDataDecoder(Decoder):
    parameters: InitVar[Mapping[str, Any]]
    NORMALIZED_FIELD_NAMES = ["date", "rating", "comments", "response", "order_id", "rater_email"]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        # csv header field names for this report differ per marketplace (are localized to marketplace language)
        # but columns come in the same order, so we set fieldnames to our custom ones
        # and raise error if original and custom header field count does not match
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        try:
            parsed = xmltodict.parse(
                document,
                dict_constructor=dict,
                attr_prefix="",
                cdata_key="text",
                force_list={"attribute", "id", "refinementField"},
            )
        except Exception as e:
            logger.warning(f"Unable to parse the report for the stream, error: {str(e)}")
            parsed = {}

        yield from parsed.get("Result", {}).get("Node", [])


class LedgerDetailedViewReportsTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: str, field_schema: Dict[str, Any]) -> str:
            if original_value and field_schema.get("format") == "date":
                date_format = "%m/%Y" if len(original_value) <= 7 else "%m/%d/%Y"
                try:
                    transformed_value = dt.strptime(original_value, date_format).strftime("%Y-%m-%d")
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class MerchantListingsFypReportTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                try:
                    transformed_value = ab_datetime_parse(original_value).strftime("%Y-%m-%d")
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class MerchantReportsTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date-time":
                # `dateparser` is used here because AirbyteDatetime/
                # Datetime cannot easily parse timezone abbrvs
                transformed_value = dateparser.parse(original_value).isoformat()
                return transformed_value
            return original_value

        return transform_function


class SellerFeedbackReportsTypeTransformer(TypeTransformer):
    config: Dict[str, Any] = None

    MARKETPLACE_DATE_FORMAT_MAP = dict(
        # eu
        A2VIGQ35RCS4UG="%d/%m/%y",  # AE
        A1PA6795UKMFR9="%d.%m.%y",  # DE
        A1C3SOZRARQ6R3="%d/%m/%y",  # PL
        ARBP9OOSHTCHU="%d/%m/%y",  # EG
        A1RKKUPIHCS9HS="%d/%m/%y",  # ES
        A13V1IB3VIYZZH="%d/%m/%y",  # FR
        A21TJRUUN4KGV="%d/%m/%y",  # IN
        APJ6JRA9NG5V4="%d/%m/%y",  # IT
        A1805IZSGTT6HS="%d/%m/%y",  # NL
        A17E79C6D8DWNP="%d/%m/%y",  # SA
        A2NODRKZP88ZB9="%Y-%m-%d",  # SE
        A33AVAJ2PDY3EV="%d/%m/%y",  # TR
        A1F83G8C2ARO7P="%d/%m/%y",  # UK
        A28R8C7NBKEWEA="%d/%m/%y",  # IE
        AMEN7PMS3EDWL="%d/%m/%y",  # BE
        # fe
        A39IBJ37TRP1C6="%d/%m/%y",  # AU
        A1VC38T7YXB528="%y/%m/%d",  # JP
        A19VAU5U5O7RUS="%d/%m/%y",  # SG
        # na
        ATVPDKIKX0DER="%m/%d/%y",  # US
        A2Q3Y263D00KWC="%d/%m/%y",  # BR
        A2EUQ1WTGCTBG2="%d/%m/%y",  # CA
        A1AM78C64UM0Y8="%d/%m/%y",  # MX
    )

    def __init__(self, *args, config, **kwargs):
        self.marketplace_id = config.get("marketplace_id")
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    def get_transform_function(self):
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                date_format = self.MARKETPLACE_DATE_FORMAT_MAP.get(self.marketplace_id)
                # Checks if the date is already in the target format -- this will be the case for dataEndTime field
                try:
                    dt.strptime(original_value, "%Y-%m-%d")
                    return original_value
                except ValueError:
                    pass
                if not date_format:
                    raise KeyError(f"Date format not found for Marketplace ID: {self.marketplace_id}")
                try:
                    return dt.strptime(original_value, date_format).strftime("%Y-%m-%d")
                except ValueError as e:
                    raise ValueError(
                        f"Error parsing date: {original_value} is expected to be in format {date_format} for marketplace_id: {self.marketplace_id}"
                    ) from e

            return original_value

        return transform_function


class FlatFileSettlementV2ReportsTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value == "" and field_schema.get("format") == "date-time":
                return None
            return original_value

        return transform_function


class RateLimitConfigErrorHttpClient(HttpClient):
    """Custom HttpClient that surfaces rate limit exhaustion as a config error with troubleshooting guidance."""

    _TROUBLESHOOTING_DOCS_URL = "https://docs.airbyte.com/integrations/sources/amazon-seller-partner#rate-limit-issue-for-report-streams"

    def _send_with_retry(
        self,
        request: requests.PreparedRequest,
        request_kwargs: Mapping[str, Any],
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
        exit_on_rate_limit: Optional[bool] = False,
    ) -> requests.Response:
        try:
            return super()._send_with_retry(request, request_kwargs, log_formatter, exit_on_rate_limit)
        except AirbyteTracedException as e:
            if e.failure_type == FailureType.transient_error and "Rate limit retry budget exhausted" in (e.internal_message or ""):
                raise AirbyteTracedException(
                    internal_message=e.internal_message,
                    message=(
                        f"Rate limit retry budget exhausted. "
                        f"Adjust your connector configuration to reduce API request volume. "
                        f"See troubleshooting steps at {self._TROUBLESHOOTING_DOCS_URL}"
                    ),
                    failure_type=FailureType.config_error,
                    exception=e._exception,
                    stream_descriptor=e._stream_descriptor,
                ) from e
            raise


@dataclass
class ReportCreationRequester(HttpRequester):
    """
    Custom HttpRequester for Amazon SP-API report creation that checks for existing reports
    before creating new ones. This avoids hitting Amazon's strict per-report-type rate limits
    (undocumented ~30-minute cooldown) by reusing reports that are already in progress or completed.

    Flow:
    1. Before creating a new report via POST, call GET /reports to check for existing reports
       of the same reportType, matching date range, and marketplaceIds.
    2. If matching reports are found, select the most recently created one (by createdTime).
       DONE reports older than `max_done_report_age_hours` (from config, default 0) are skipped
       since their data snapshot may be stale and the report document may have expired. When the
       config value is 0 (default), DONE reports are never reused. Status filtering (e.g.
       CANCELLED, FATAL) is done here to prevent reuse of reports that should not be reused.
       The manifest's status_mapping remains the single source of truth for which statuses
       are retryable, skippable, or terminal once a report is being polled.
    3. If no suitable report is found, fall through to super().send_request() to create a new one.
    """

    request_body_json: Optional[Dict[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        if self.config.get("stop_sync_on_rate_limit", False):
            self._http_client = RateLimitConfigErrorHttpClient(
                name=self.name,
                logger=self.logger,
                error_handler=self.error_handler,
                api_budget=self.api_budget,
                authenticator=self._authenticator,
                use_cache=self.use_cache,
                backoff_strategy=getattr(self.error_handler, "backoff_strategies", None),
                disable_retries=self.disable_retries,
                message_repository=self.message_repository,
            )
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config, parameters=parameters, request_body_json=self.request_body_json
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider

    def send_request(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Any] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        # Extract reportType and date range from the request body JSON that would be sent to createReport
        body_json = self._request_body_json(stream_state, stream_slice, next_page_token, request_body_json)
        report_type = body_json.get("reportType", "") if body_json else ""
        requested_start = body_json.get("dataStartTime", "") if body_json else ""
        requested_end = body_json.get("dataEndTime", "") if body_json else ""
        requested_marketplace_ids = body_json.get("marketplaceIds", []) if body_json else []

        if report_type:
            existing_report = self._find_existing_report(
                stream_state=stream_state,
                stream_slice=stream_slice,
                report_type=report_type,
                requested_start=requested_start,
                requested_end=requested_end,
                requested_marketplace_ids=requested_marketplace_ids,
            )
            if existing_report is not None:
                return existing_report

        # No existing report found — create a new one via the normal POST flow
        return super().send_request(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            path=path,
            request_headers=request_headers,
            request_params=request_params,
            request_body_data=request_body_data,
            request_body_json=request_body_json,
            log_formatter=log_formatter,
        )

    def _fetch_reports(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Any],
        report_type: str,
        marketplace_ids: List[str],
    ) -> Tuple[List[Dict[str, Any]], Optional[requests.Response]]:
        """
        Query GET /reports to retrieve the list of existing reports for the given reportType
        and marketplaceIds. Results are sorted by createdTime descending (newest first) by the API.
        Uses pageSize=100 (max) to get the most complete first page.
        Returns a tuple of (reports_list, original_response). Returns ([], None) on any error.
        """
        try:
            url_base = self.get_url_base(stream_state=stream_state, stream_slice=stream_slice)
            get_url = self._join_url(url_base, "reports/2021-06-30/reports")
            headers = self._request_headers(stream_state, stream_slice, None, {"content-type": "application/json"})
            params: Dict[str, Any] = {
                "reportTypes": report_type,
                "pageSize": 100,
            }
            if marketplace_ids:
                params["marketplaceIds"] = ",".join(marketplace_ids)
            _, get_response = self._http_client.send_request(
                http_method="GET",
                url=get_url,
                request_kwargs={"stream": False},
                headers=headers,
                params=params,
            )
        except Exception:
            logger.warning(
                f"Failed to query existing reports for {report_type}. Will create a new report.",
                exc_info=True,
            )
            return [], None

        if not get_response or not get_response.ok:
            return [], None

        try:
            data = get_response.json()
        except (json.JSONDecodeError, ValueError):
            return [], None

        return data.get("reports", []), get_response

    def _find_existing_report(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Any],
        report_type: str,
        requested_start: str,
        requested_end: str,
        requested_marketplace_ids: List[str],
    ) -> Optional[requests.Response]:
        """
        Find an existing report matching the given reportType, date range, and marketplaceIds.
        Returns a synthetic Response wrapping the first matching report if found, or None.

        The API returns reports sorted by createdTime descending (newest first), and we
        filter by reportType and marketplaceIds in the query params, so the first match
        in the iteration is the most recently created matching report.

        CANCELLED reports are skipped so that a new report is always created for them.
        This acts as a retry mechanism: if the data is now available, the new report will
        succeed; if still no data, the new report will also be CANCELLED and the CDK's
        SKIPPED status mapping will handle it silently.

        FATAL reports are also skipped because they represent permanently failed report
        processing by Amazon. Reusing a FATAL report would cause the CDK's status_mapping
        (which maps FATAL to `failed`) to trigger a retry, which would find the same
        FATAL report again, creating an infinite loop.
        """
        reports, get_response = self._fetch_reports(stream_state, stream_slice, report_type, requested_marketplace_ids)
        if not reports:
            return None

        for report in reports:
            if not self._date_ranges_match(requested_start, requested_end, report):
                continue

            if not self._is_report_fresh(report, report_type):
                continue

            report_status = report.get("processingStatus", "")
            if report_status == "CANCELLED":
                logger.info(
                    f"Skipping CANCELLED report {report.get('reportId', '')} for {report_type}. "
                    f"A new report will be created to retry in case data is now available."
                )
                continue

            if report_status == "FATAL":
                logger.info(
                    f"Skipping FATAL report {report.get('reportId', '')} for {report_type}. "
                    f"A new report will be created instead of reusing a permanently failed one."
                )
                continue

            # First matching report is the most recently created (API sorts by createdTime desc)
            report_id = report.get("reportId", "")
            report_start = report.get("dataStartTime", "")
            report_end = report.get("dataEndTime", "")
            logger.info(
                f"Found existing report {report_id} (status={report_status}) "
                f"for {report_type} [{report_start} - {report_end}]. Reusing instead of creating a new one."
            )
            return self._build_synthetic_response(report, get_response)

        return None

    def _is_report_fresh(
        self,
        report: Dict[str, Any],
        report_type: str,
    ) -> bool:
        """
        Check whether a DONE report is fresh enough to reuse.

        Reads max_done_report_age_hours from config (default 0).
        When max_done_report_age_hours is 0 (default), DONE reports are never reused —
        only IN_QUEUE / IN_PROGRESS reports pass through.
        When max_done_report_age_hours > 0, DONE reports older than that threshold are skipped.
        Non-DONE reports (IN_QUEUE, IN_PROGRESS, etc.) are always considered fresh.
        """
        report_status = report.get("processingStatus", "")
        if report_status != "DONE":
            return True

        max_done_report_age_hours = self.config.get("max_done_report_age_hours", 0)
        report_id = report.get("reportId", "")
        if max_done_report_age_hours == 0:
            logger.info(
                f"Skipping DONE report {report_id} for {report_type} because max_done_report_age_hours is 0 (always create new reports)."
            )
            return False

        created_time_str = report.get("createdTime", "")
        if created_time_str:
            try:
                created_time = ab_datetime_parse(created_time_str)
                age_hours = (ab_datetime_now() - created_time).total_seconds() / 3600
                if age_hours > max_done_report_age_hours:
                    logger.info(
                        f"Skipping stale DONE report {report_id} (created {age_hours:.1f}h ago) "
                        f"for {report_type}. Will look for a newer one."
                    )
                    return False
            except (ValueError, TypeError):
                pass  # If we can't parse createdTime, don't skip — still usable

        return True

    @staticmethod
    def _date_ranges_match(
        requested_start: str,
        requested_end: str,
        report: Dict[str, Any],
    ) -> bool:
        """
        Compare requested date range with a report's date range.
        Extracts dataStartTime/dataEndTime from the report.
        Both sides use ISO 8601 format from the Amazon SP-API.
        We compare full datetime values (including hours, minutes, seconds)
        to ensure exact match of the requested time range.
        """
        report_start = report.get("dataStartTime", "")
        report_end = report.get("dataEndTime", "")
        if not report_start or not report_end:
            return False
        try:
            req_start_dt = ab_datetime_parse(requested_start) if requested_start else None
            req_end_dt = ab_datetime_parse(requested_end) if requested_end else None
            rep_start_dt = ab_datetime_parse(report_start)
            rep_end_dt = ab_datetime_parse(report_end)

            if req_start_dt is None or req_end_dt is None:
                return False

            return req_start_dt == rep_start_dt and req_end_dt == rep_end_dt
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _build_synthetic_response(report: Dict[str, Any], original_response: requests.Response) -> requests.Response:
        """
        Build a synthetic requests.Response that looks like a createReport response,
        containing the reportId from the existing report. The polling_requester uses
        creation_response['reportId'] to poll the report status.
        """
        synthetic = requests.Response()
        synthetic.status_code = 200
        synthetic.headers.update(original_response.headers)
        # The createReport response normally returns {"reportId": "..."}.
        # We return the same structure so the polling_requester can use creation_response['reportId'].
        synthetic._content = json.dumps({"reportId": report["reportId"]}).encode("utf-8")
        return synthetic


# Report options Amazon documents as required for a given report type. Used only to make the
# error message actionable when Amazon rejects a report - the connector never fills these in
# on the user's behalf, so a report that Amazon accepts today keeps being requested unchanged.
# https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics
REQUIRED_REPORT_OPTIONS: Mapping[str, Tuple[str, ...]] = {
    "GET_VENDOR_SALES_REPORT": ("reportPeriod", "distributorView", "sellingProgram"),
    "GET_VENDOR_INVENTORY_REPORT": ("reportPeriod", "distributorView", "sellingProgram"),
    "GET_VENDOR_TRAFFIC_REPORT": ("reportPeriod",),
    "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT": ("reportPeriod",),
}

# Lower-cased substrings in Amazon's FATAL error document that identify a reportOptions problem.
# Amazon's wording is not stable, so this is a best-effort match: a miss only means the sync fails
# with Amazon's message logged rather than as a config error.
# "reportoption" is singular on purpose: Amazon's observed wording is "requires the <names>
# reportOption to be specified", and the singular form also matches the plural spelling. Matching
# only the option names would miss this sentence for any option not listed in
# REQUIRED_REPORT_OPTIONS.
_REPORT_OPTIONS_ERROR_MARKERS = (
    "reportoption",
    "report options",
    "reportperiod",
    "distributorview",
    "sellingprogram",
    "invalid report option",
    "missing required option",
)

# Amazon's error text still refers users to amzn/selling-partner-api-docs, archived in June 2024.
_REPORT_OPTIONS_DOC_URL = "https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics"

# Cap on how much of Amazon's error document is echoed into logs and error messages.
_MAX_FAILURE_REASON_CHARS = 500


@dataclass
class ReportPollingRequester(HttpRequester):
    """
    Polling requester for Amazon SP-API reports that surfaces why a report failed.

    When `getReport` returns `processingStatus: FATAL`, Amazon accepted the `createReport` call but
    could not produce the report, and the reason lives in a separate error document referenced by
    `reportDocumentId`. The CDK never fetches that document: it just retries and eventually fails the
    sync with "Async job failed after exhausting all retry attempts." and `failure_type=system_error`,
    which tells the user nothing and looks like an Airbyte bug.

    This requester fetches the error document on FATAL and:
      - always logs Amazon's reason at ERROR, so it appears in the sync logs; and
      - raises a `config_error` when the reason points at reportOptions, naming the options Amazon
        documents as required for that report type. `AsyncJobOrchestrator._is_breaking_exception`
        treats a `config_error` as breaking, so the sync aborts immediately with that message
        instead of burning through `failed_retry_wait_time_in_seconds` (default 1800s) retries.

    Anything else - a missing document, a fetch failure, an unrecognised payload - leaves the
    response untouched so the existing retry and status-mapping behaviour is unchanged. This is a
    diagnostic path only: it never turns a report Amazon accepted into a failure.
    """

    # HttpRequester has no request_headers field: for a CustomRequester the factory does not build a
    # request_options_provider from the manifest, so the field must be declared and the provider built
    # here or the manifest's content-type header is silently dropped from every polling request.
    # Same workaround ReportCreationRequester applies for request_body_json.
    request_headers: Optional[Dict[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config, parameters=parameters, request_headers=self.request_headers
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider

    def send_request(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Any] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        response = super().send_request(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
            path=path,
            request_headers=request_headers,
            request_params=request_params,
            request_body_data=request_body_data,
            request_body_json=request_body_json,
            log_formatter=log_formatter,
        )
        if response is None:
            return response

        try:
            body = response.json()
        except (json.JSONDecodeError, ValueError):
            return response
        if not isinstance(body, dict) or body.get("processingStatus") != "FATAL":
            return response

        report_type = body.get("reportType") or "report"
        report_id = body.get("reportId") or "unknown"
        document_id = body.get("reportDocumentId")

        reason = None
        if document_id:
            reason = self._fetch_failure_reason(stream_state, stream_slice, document_id)

        if not reason:
            logger.error(
                f"Amazon returned processingStatus FATAL for {report_type} (reportId {report_id}) "
                f"without an error document explaining why."
            )
            return response

        logger.error(f"Amazon returned processingStatus FATAL for {report_type} (reportId {report_id}): {reason}")

        if self._is_report_options_error(reason):
            raise AirbyteTracedException(
                internal_message=f"FATAL report {report_id} ({report_type}): {reason}",
                message=self._report_options_error_message(report_type, reason),
                failure_type=FailureType.config_error,
            )
        return response

    def _fetch_failure_reason(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Any],
        document_id: str,
    ) -> Optional[str]:
        """
        Resolve `reportDocumentId` to a download URL via the documents endpoint, download the error
        document, and pull Amazon's message out of it. Returns None if anything goes wrong: this is
        best-effort diagnostics and must never be the reason a sync fails.
        """
        try:
            url_base = self.get_url_base(stream_state=stream_state, stream_slice=stream_slice)
            document_url = self._join_url(url_base, f"reports/2021-06-30/documents/{document_id}")
            # No extra headers here: the manifest already supplies content-type through the
            # request options provider, and combine_mappings rejects a duplicate key.
            headers = self._request_headers(stream_state, stream_slice, None)
            _, document_response = self._http_client.send_request(
                http_method="GET",
                url=document_url,
                request_kwargs={"stream": False},
                headers=headers,
            )
            if not document_response or not document_response.ok:
                return None
            document = document_response.json()
            download_url = document.get("url")
            if not download_url:
                return None

            # The download URL is pre-signed; sending SP-API auth headers with it is rejected,
            # which is why the manifest's download_requester uses NoAuth. Use a bare request here.
            download_response = requests.get(download_url, timeout=60)
            if not download_response.ok:
                return None
            payload = self._decode_document(download_response, document.get("compressionAlgorithm"))
        except Exception:
            logger.warning(f"Could not retrieve the error document for FATAL report document {document_id}.", exc_info=True)
            return None

        return self._extract_message(payload)

    @staticmethod
    def _decode_document(response: requests.Response, compression_algorithm: Optional[str]) -> str:
        """Decode the error document, tolerating a compressionAlgorithm that does not match the payload."""
        if (compression_algorithm or "").upper() == "GZIP":
            try:
                return gzip.decompress(response.content).decode("utf-8", errors="replace")
            except (OSError, EOFError, gzip.BadGzipFile):
                pass
        return response.text

    @staticmethod
    def _extract_message(payload: Optional[str]) -> Optional[str]:
        """
        Pull a human-readable message out of an Amazon error document. The payload may be a JSON
        object, a JSON error envelope, or plain text, so fall back to the raw text when in doubt.
        """
        if not payload or not payload.strip():
            return None
        text = payload.strip()

        try:
            document = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            first_line = next((line.strip() for line in text.splitlines() if line.strip()), None)
            return first_line[:_MAX_FAILURE_REASON_CHARS] if first_line else None

        if isinstance(document, dict):
            for key in ("errorDetails", "errorMessage", "message", "reason"):
                value = document.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()[:_MAX_FAILURE_REASON_CHARS]
            errors = document.get("errors")
            if isinstance(errors, list):
                messages = [
                    error["message"].strip()
                    for error in errors
                    if isinstance(error, dict) and isinstance(error.get("message"), str) and error["message"].strip()
                ]
                if messages:
                    return "; ".join(messages)[:_MAX_FAILURE_REASON_CHARS]
        return text[:_MAX_FAILURE_REASON_CHARS]

    @staticmethod
    def _is_report_options_error(reason: str) -> bool:
        lowered = reason.lower()
        return any(marker in lowered for marker in _REPORT_OPTIONS_ERROR_MARKERS)

    @staticmethod
    def _report_options_error_message(report_type: str, reason: str) -> str:
        """
        Quote Amazon once, then say what to do once. Amazon's reason normally names the options it
        wants, so REQUIRED_REPORT_OPTIONS is only a fallback for when it does not: restating a
        hardcoded list alongside Amazon's own would contradict the quote the moment the two diverge.
        """
        lowered = reason.lower()
        documented = REQUIRED_REPORT_OPTIONS.get(report_type, ())
        if documented and not any(option.lower() in lowered for option in documented):
            which = f"Amazon documents {', '.join(documented)} as required for this report. "
        else:
            which = ""
        # Amazon's own text may point at its retired GitHub docs, so correct that where it appears.
        doc_reference = "Amazon's GitHub docs were archived in 2024; see " if "github" in lowered else "See "
        return (
            f'Amazon rejected the {report_type} report request. Amazon\'s reason: "{reason}" '
            f"{which}"
            f"Add the options under Report Options in the source settings: set Report Name and "
            f"Stream Name to {report_type}, then one Name/Value pair per option. Names and values "
            f"are case-sensitive. {doc_reference}{_REPORT_OPTIONS_DOC_URL}"
        )


@dataclass
class ValidateReportOptionsListStreamNameUniqueness(ValidationStrategy):
    """
    Validate that stream names are unique across all report options in `report_options_list`.
    """

    def validate(self, value: Any) -> None:
        report_options_list = value
        if not isinstance(report_options_list, list) or len(report_options_list) == 0:
            return
        stream_names = []
        for report_option in report_options_list:
            if report_option["stream_name"] in stream_names:
                raise ValueError(
                    f"Stream names (`stream_name`) should be unique across all report options in `report_options_list`. Duplicate value: {report_option['stream_name']}"
                )
            stream_names.append(report_option["stream_name"])


@dataclass
class ValidateReportOptionsListOptionNameUniqueness(ValidationStrategy):
    """
    Validate that option names are unique across all options within a report option's `options_list`.
    """

    def validate(self, value: Any) -> None:
        report_options_list = value
        if isinstance(report_options_list, list) and len(report_options_list) > 0 and isinstance(report_options_list[0], dict):
            for report_options in report_options_list:
                option_names = []
                for option in report_options["options_list"]:
                    if option["option_name"] in option_names:
                        raise ValueError(
                            f"Option names (`option_name`) should be unique across all options in `options_list`. Duplicate value: {option['option_name']}"
                        )
                    option_names.append(option["option_name"])
