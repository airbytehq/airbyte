#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import csv
import gzip
import json
import logging
from dataclasses import InitVar, dataclass
from datetime import datetime as dt
from io import StringIO
from typing import Any, Dict, Generator, List, Mapping, MutableMapping, Optional, Union

import dateparser
import requests
import xmltodict

from airbyte_cdk import HttpMethod, HttpRequester, InterpolatedString, LimiterSession, NoAuth
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.validators.validation_strategy import ValidationStrategy
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.types import EmptyString
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse


logger = logging.getLogger("airbyte")


@dataclass
class AmazonSPOauthAuthenticator(DeclarativeOauth2Authenticator):
    """
    This class extends the DeclarativeOauth2Authenticator functionality
    and allows to pass custom headers to the refresh access token requests
    """

    host: Union[InterpolatedString, str] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        super().__post_init__(parameters)
        self._host = InterpolatedString.create(self.host, parameters=parameters)

    def get_auth_header(self) -> Mapping[str, Any]:
        return {
            "host": self._host.eval(self.config),
            "user-agent": "python-requests",
            "x-amz-access-token": self.get_access_token(),
            "x-amz-date": ab_datetime_now().strftime("%Y%m%dT%H%M%SZ"),
        }

    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        return {"Content-Type": "application/x-www-form-urlencoded"}


@dataclass
class AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy(WaitTimeFromHeaderBackoffStrategy):
    """
    This strategy is designed for scenarios where the server communicates retry-after durations
    through HTTP headers. The wait time is derived by taking the reciprocal of the value extracted
    from the header. If the header does not provide a valid time, a default backoff time is used.
    """

    default_backoff_time: Optional[float] = 10

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int,
    ) -> Optional[float]:
        time_from_header = super().backoff_time(response_or_exception, attempt_count)
        if time_from_header:
            return 1 / float(time_from_header)
        else:
            return self.default_backoff_time


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
            logger.warning(f"Unable to parse the report for the stream {self.name}, error: {str(e)}")
            return []

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


class CreationLimiterSession(LimiterSession):
    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        """Send a request with rate-limiting."""
        self._api_budget.acquire_call(request)
        """
        Refresh access token if after waiting it was expired.
        Especially, needed for GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL report 
        due to waiting limit time for create report operation is 1 request per 30 minutes.
        """
        if self.auth.token_has_expired():
            updated_token = self.auth.get_auth_header()
            request.headers.update(updated_token)

        response = super().send(request, **kwargs)
        self._api_budget.update_from_response(request, response)
        return response


class CreationHttpClient(HttpClient):
    def _request_session(self) -> requests.Session:
        return CreationLimiterSession(api_budget=self._api_budget)


@dataclass
class CreationCustomRequester(HttpRequester):
    request_headers: Optional[str] = None
    request_body_json: Optional[Mapping[str, Any]] = None
    api_budget: Optional[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._url = InterpolatedString.create(self.url if self.url else EmptyString, parameters=parameters)
        # deprecated
        self._url_base = InterpolatedString.create(self.url_base if self.url_base else EmptyString, parameters=parameters)
        # deprecated
        self._path = InterpolatedString.create(self.path if self.path else EmptyString, parameters=parameters)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config, request_headers=self.request_headers, request_body_json=self.request_body_json, parameters=parameters
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self._authenticator = self.authenticator or NoAuth(parameters=parameters)
        self._http_method = HttpMethod[self.http_method] if isinstance(self.http_method, str) else self.http_method
        self.error_handler = self.error_handler
        self._parameters = parameters

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies  # type: ignore
        else:
            backoff_strategies = None

        self._http_client = CreationHttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            api_budget=self.api_budget,
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )
