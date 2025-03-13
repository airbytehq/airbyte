#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from datetime import timedelta
from functools import cached_property, lru_cache
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union

import backoff
import pendulum as pendulum
import requests
from requests import HTTPError, codes

from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException
from source_hubspot.components import NewtoLegacyFieldTransformation
from source_hubspot.constants import OAUTH_CREDENTIALS, PRIVATE_APP_CREDENTIALS
from source_hubspot.errors import HubspotAccessDenied, HubspotInvalidAuth, HubspotRateLimited, HubspotTimeout, InvalidStartDateConfigError
from source_hubspot.helpers import (
    APIPropertiesWithHistory,
    APIv1Property,
    APIv2Property,
    APIv3Property,
    GroupByKey,
    IRecordPostProcessor,
    IURLPropertyRepresentation,
    StoreAsIs,
)


# we got this when provided API Token has incorrect format
CLOUDFLARE_ORIGIN_DNS_ERROR = 530

VALID_JSON_SCHEMA_TYPES = {
    "string",
    "integer",
    "number",
    "boolean",
    "object",
    "array",
}

KNOWN_CONVERTIBLE_SCHEMA_TYPES = {
    "bool": ("boolean", None),
    "enumeration": ("string", None),
    "date": ("string", "date"),
    "date-time": ("string", "date-time"),
    "datetime": ("string", "date-time"),
    "json": ("string", None),
    "phone_number": ("string", None),
}

CUSTOM_FIELD_TYPE_TO_VALUE = {
    bool: "boolean",
    str: "string",
    float: "number",
    int: "integer",
}

CUSTOM_FIELD_VALUE_TO_TYPE = {v: k for k, v in CUSTOM_FIELD_TYPE_TO_VALUE.items()}

CONTACTS_NEW_TO_LEGACY_FIELDS_MAPPING = {
    "hs_lifecyclestage_": "hs_v2_date_entered_",
    "hs_date_exited_": "hs_v2_date_exited_",
    "hs_time_in_": "hs_v2_latest_time_in_",
}

DEALS_NEW_TO_LEGACY_FIELDS_MAPPING = {
    "hs_date_entered_": "hs_v2_date_entered_",
    "hs_date_exited_": "hs_v2_date_exited_",
    "hs_time_in_": "hs_v2_latest_time_in_",
}


def retry_token_expired_handler(**kwargs):
    """Retry helper when token expired"""

    return backoff.on_exception(
        backoff.expo,
        HubspotInvalidAuth,
        **kwargs,
    )


class RecordUnnester:
    def __init__(self, fields: Optional[List[str]] = None):
        self.fields = fields or []

    def unnest(self, records: Iterable[MutableMapping[str, Any]]) -> Iterable[MutableMapping[str, Any]]:
        """
        In order to not make the users query their destinations for complicated json fields, duplicate some nested data as top level fields.
        For instance:
        {"id": 1, "updatedAt": "2020-01-01", "properties": {"hs_note_body": "World's best boss", "hs_created_by": "Michael Scott"}}
        becomes
        {
            "id": 1,
            "updatedAt": "2020-01-01",
            "properties": {"hs_note_body": "World's best boss", "hs_created_by": "Michael Scott"},
            "properties_hs_note_body": "World's best boss",
            "properties_hs_created_by": "Michael Scott"
        }
        """

        for record in records:
            fields_to_unnest = self.fields + ["properties"]
            data_to_unnest = {field: record.get(field, {}) for field in fields_to_unnest}
            unnested_data = {
                f"{top_level_name}_{name}": value for (top_level_name, data) in data_to_unnest.items() for (name, value) in data.items()
            }
            final = {**record, **unnested_data}
            yield final


def retry_connection_handler(**kwargs):
    """Retry helper, log each attempt"""

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def giveup_handler(exc):
        if isinstance(exc, json.decoder.JSONDecodeError):
            return False
        if isinstance(exc, (HubspotInvalidAuth, HubspotAccessDenied)):
            return True
        return exc.response is not None and HTTPStatus.BAD_REQUEST <= exc.response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR

    return backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        jitter=None,
        on_backoff=log_retry_attempt,
        giveup=giveup_handler,
        **kwargs,
    )


def retry_after_handler(fixed_retry_after=None, **kwargs):
    """Retry helper when we hit the call limit, sleeps for specific duration"""

    def sleep_on_ratelimit(_details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HubspotRateLimited):
            # HubSpot API does not always return Retry-After value for 429 HTTP error
            retry_after = fixed_retry_after if fixed_retry_after else int(exc.response.headers.get("Retry-After", 3))
            logger.info(f"Rate limit reached. Sleeping for {retry_after} seconds")
            time.sleep(retry_after + 1)  # extra second to cover any fractions of second

    def log_giveup(_details):
        logger.error("Max retry limit reached")

    return backoff.on_exception(
        backoff.constant,
        HubspotRateLimited,
        jitter=None,
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_giveup,
        interval=0,  # skip waiting part, we will wait in on_backoff handler
        **kwargs,
    )


class HubspotAvailabilityStrategy(HttpAvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
        """Catch HTTPError thrown from parent stream which is called by get_first_stream_slice"""
        try:
            return super().check_availability(stream, logger, source)
        except HTTPError as error:
            is_available, reason = self.handle_http_error(stream, logger, source, error)
            if reason:
                reason = f"Unable to sync stream '{stream.name}' because of permission error in parent stream. {reason}"
            return is_available, reason


class API:
    """HubSpot API interface, authorize, retrieve and post, supports backoff logic."""

    BASE_URL = "https://api.hubapi.com"
    USER_AGENT = "Airbyte"
    logger = logger

    def is_oauth2(self) -> bool:
        credentials_title = self.credentials.get("credentials_title")

        return credentials_title == OAUTH_CREDENTIALS

    def is_private_app(self) -> bool:
        credentials_title = self.credentials.get("credentials_title")

        return credentials_title == PRIVATE_APP_CREDENTIALS

    def get_authenticator(self) -> Optional[Oauth2Authenticator]:
        if self.is_oauth2():
            return Oauth2Authenticator(
                token_refresh_endpoint=self.BASE_URL + "/oauth/v1/token",
                client_id=self.credentials["client_id"],
                client_secret=self.credentials["client_secret"],
                refresh_token=self.credentials["refresh_token"],
            )
        elif self.is_private_app():
            return TokenAuthenticator(token=self.credentials["access_token"])
        else:
            return None

    def __init__(self, credentials: Mapping[str, Any]):
        self._session = requests.Session()
        self.credentials = credentials

        if self.is_oauth2() or self.is_private_app():
            self._session.auth = self.get_authenticator()
        else:
            raise Exception("No supported `credentials_title` specified. See spec.yaml for references")

        self._session.headers = {
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }

    @staticmethod
    def _parse_and_handle_errors(response) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        """Handle response"""
        message = "Unknown error"
        if response.headers.get("content-type") == "application/json;charset=utf-8" and response.status_code != HTTPStatus.OK:
            message = response.json().get("message")

        if response.status_code == HTTPStatus.BAD_REQUEST:
            message = f"Request to {response.url} didn't succeed. Please verify your credentials and try again.\nError message from Hubspot API: {message}"
            logger.warning(message)
        elif response.status_code == HTTPStatus.FORBIDDEN:
            message = f"The authenticated user does not have permissions to access the URL {response.url}. Verify your permissions to access this endpoint."
            logger.warning(message)
        elif response.status_code in (HTTPStatus.UNAUTHORIZED, CLOUDFLARE_ORIGIN_DNS_ERROR):
            message = (
                "The user cannot be authorized with provided credentials. Please verify that your credentails are valid and try again."
            )
            raise HubspotInvalidAuth(internal_message=message, failure_type=FailureType.config_error, response=response)
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            message = f"You have reached your Hubspot API limit. We will resume replication once after {retry_after} seconds.\nSee https://developers.hubspot.com/docs/api/usage-details"
            raise HubspotRateLimited(
                message,
                response=response,
            )
        elif response.status_code in (HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE):
            raise HubspotTimeout(message, response)
        else:
            response.raise_for_status()

        return response.json()

    @retry_connection_handler(max_tries=5, factor=5)
    @retry_after_handler(max_tries=3)
    def get(
        self, url: str, params: MutableMapping[str, Any] = None
    ) -> Tuple[Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]], requests.Response]:
        response = self._session.get(self.BASE_URL + url, params=params)
        return self._parse_and_handle_errors(response), response

    def post(
        self, url: str, data: Mapping[str, Any], params: MutableMapping[str, Any] = None
    ) -> Tuple[Union[Mapping[str, Any], List[Mapping[str, Any]]], requests.Response]:
        response = self._session.post(self.BASE_URL + url, params=params, json=data)
        return self._parse_and_handle_errors(response), response

    def get_custom_objects_metadata(self) -> Iterable[Tuple[str, str, Mapping[str, Any]]]:
        data, response = self.get("/crm/v3/schemas", {})
        if not response.ok or "results" not in data:
            self.logger.warn(self._parse_and_handle_errors(response))
            return ()
        for metadata in data["results"]:
            properties = self.get_properties(raw_schema=metadata)
            schema = self.generate_schema(properties)
            yield metadata["name"], metadata["fullyQualifiedName"], schema, properties

    def get_properties(self, raw_schema: Mapping[str, Any]) -> Mapping[str, Any]:
        return {field["name"]: self._field_to_property_schema(field) for field in raw_schema["properties"]}

    def generate_schema(self, properties: Mapping[str, Any]) -> Mapping[str, Any]:
        unnested_properties = {f"properties_{property_name}": property_value for (property_name, property_value) in properties.items()}
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": {
                "id": {"type": ["null", "string"]},
                "createdAt": {"type": ["null", "string"], "format": "date-time"},
                "updatedAt": {"type": ["null", "string"], "format": "date-time"},
                "archived": {"type": ["null", "boolean"]},
                "properties": {"type": ["null", "object"], "properties": properties},
                **unnested_properties,
            },
        }

        return schema

    def _field_to_property_schema(self, field: Dict[str, Any]) -> Mapping[str, Any]:
        field_type = field["type"]
        property_schema = {}
        if field_type == "enumeration" or field_type == "string":
            property_schema = {"type": ["null", "string"]}
        elif field_type == "datetime" or field_type == "date":
            property_schema = {"type": ["null", "string"], "format": "date-time"}
        elif field_type == "number":
            property_schema = {"type": ["null", "number"]}
        elif field_type == "boolean" or field_type == "bool":
            property_schema = {"type": ["null", "boolean"]}
        else:
            self.logger.warn(f"Field {field['name']} has unrecognized type: {field['type']} casting to string.")
            property_schema = {"type": ["null", "string"]}

        return property_schema


class Stream(HttpStream, ABC):
    """Base class for all streams. Responsible for data fetching and pagination"""

    entity: str = None
    cast_fields: List = None
    updated_at_field: str = None
    created_at_field: str = None

    more_key: str = None
    data_field = "results"

    page_filter = "offset"
    page_field = "offset"
    limit_field = "limit"
    limit = 100
    offset = 0
    primary_key = None
    filter_old_records: bool = True
    denormalize_records: bool = False  # one record from API response can result in multiple records emitted
    granted_scopes: Set = None
    properties_scopes: Set = None
    unnest_fields: Optional[List[str]] = None
    checkpoint_by_page = False
    _transformations: Optional[List[RecordTransformation]] = None

    @cached_property
    def record_unnester(self):
        return RecordUnnester(self.unnest_fields)

    @property
    @abstractmethod
    def scopes(self) -> Set[str]:
        """Set of required scopes. Users need to grant at least one of the scopes for the stream to be avaialble to them"""

    def scope_is_granted(self, granted_scopes: Set[str]) -> bool:
        self.granted_scopes = set(granted_scopes)
        if not self.scopes:
            return True
        else:
            return len(self.scopes.intersection(granted_scopes)) > 0

    @property
    def url_base(self) -> str:
        return "https://api.hubapi.com"

    @property
    @abstractmethod
    def url(self):
        """Default URL to read from"""

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> str:
        return self.url

    @cached_property
    def _property_wrapper(self) -> IURLPropertyRepresentation:
        properties = list(self.properties.keys())
        if "v1" in self.url:
            return APIv1Property(properties)
        if "v2" in self.url:
            return APIv2Property(properties)
        return APIv3Property(properties)

    def __init__(
        self,
        api: API,
        start_date: Union[str, pendulum.datetime],
        credentials: Mapping[str, Any] = None,
        acceptance_test_config: Mapping[str, Any] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._api: API = api
        self._credentials = credentials

        self._start_date = start_date
        if isinstance(self._start_date, str):
            try:
                self._start_date = pendulum.parse(self._start_date)
            except pendulum.parsing.exceptions.ParserError as e:
                raise InvalidStartDateConfigError(self._start_date, e)
        creds_title = self._credentials["credentials_title"]
        if creds_title in (OAUTH_CREDENTIALS, PRIVATE_APP_CREDENTIALS):
            self._authenticator = api.get_authenticator()

        # Additional configuration is necessary for testing certain streams due to their specific restrictions.
        if acceptance_test_config is None:
            acceptance_test_config = {}
        self._is_test = self.name in acceptance_test_config
        self._acceptance_test_config = acceptance_test_config.get(self.name, {})

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            message = response.json().get("message")
            raise HubspotInvalidAuth(message, response=response)
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code == codes.too_many_requests:
            return float(response.headers.get("Retry-After", 3))

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "Content-Type": "application/json",
            "User-Agent": self._api.USER_AGENT,
        }

    def get_json_schema(self) -> Mapping[str, Any]:
        json_schema = super().get_json_schema()
        if self.properties:
            properties = {"properties": {"type": "object", "properties": self.properties}}
            unnested_properties = {
                f"properties_{property_name}": property_value for (property_name, property_value) in self.properties.items()
            }
            default_props = json_schema["properties"]
            json_schema["properties"] = {**default_props, **properties, **unnested_properties}
        return json_schema

    def update_request_properties(self, params: Mapping[str, Any], properties: IURLPropertyRepresentation) -> None:
        if properties:
            params.update(properties.as_url_param())

    @retry_token_expired_handler(max_tries=5)
    def handle_request(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> requests.Response:
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        self.update_request_properties(request_params, properties)

        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token, properties=properties),
            headers=dict(request_headers, **self._authenticator.get_auth_header()),
            params=request_params,
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        if self.use_cache:
            # use context manager to handle and store cassette metadata
            with self.cache_file as cass:
                self.cassete = cass
                # vcr tries to find records based on the request, if such records exist, return from cache file
                # else make a request and save record in cache file
                response = self._send_request(request, request_kwargs)

        else:
            response = self._send_request(request, request_kwargs)

        return response

    def _read_stream_records(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Tuple[List, Any]:
        #  TODO: Additional processing was added due to the fact that users receive 414 errors while syncing their streams
        #  (issues #3977 and #5835). We will need to fix this code when the HubSpot developers add the ability to use a special parameter
        #  to get all properties for an entity. According to HubSpot Community
        #  (https://community.hubspot.com/t5/APIs-Integrations/Get-all-contact-properties-without-explicitly-listing-them/m-p/447950)
        #  and the official documentation, this does not exist at the moment.

        group_by_pk = self.primary_key and not self.denormalize_records
        post_processor: IRecordPostProcessor = GroupByKey(self.primary_key) if group_by_pk else StoreAsIs()
        response = None

        properties = self._property_wrapper
        for chunk in properties.split():
            response = self.handle_request(
                stream_slice=stream_slice, stream_state=stream_state, next_page_token=next_page_token, properties=chunk
            )
            for record in self._transform(self.parse_response(response, stream_state=stream_state)):
                post_processor.add_record(record)

        return post_processor.flat, response

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        next_page_token = None
        yield from self.read_paged_records(next_page_token=next_page_token, stream_slice=stream_slice, stream_state=stream_state)

    def read_paged_records(
        self,
        next_page_token: Optional[Mapping[str, Any]],
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False

        try:
            while not pagination_complete:
                properties = self._property_wrapper
                if properties and properties.too_many_properties:
                    records, response = self._read_stream_records(
                        stream_slice=stream_slice,
                        stream_state=stream_state,
                        next_page_token=next_page_token,
                    )
                else:
                    response = self.handle_request(
                        stream_slice=stream_slice,
                        stream_state=stream_state,
                        next_page_token=next_page_token,
                        properties=properties,
                    )
                    records = self._transform(self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice))

                if self.filter_old_records:
                    records = self._filter_old_records(records)
                yield from self.record_unnester.unnest(records)

                next_page_token = self.next_page_token(response)
                if self.checkpoint_by_page and isinstance(self, CheckpointMixin):
                    self.state = next_page_token or {"__ab_full_refresh_sync_complete": True}
                    pagination_complete = True  # For RFR streams that checkpoint by page, a single page is read per invocation
                elif not next_page_token:
                    pagination_complete = True

            # Always return an empty generator just in case no records were ever yielded
            yield from []
        except requests.exceptions.HTTPError as e:
            response = e.response
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise AirbyteTracedException("The authentication to HubSpot has expired. Re-authenticate to restore access to HubSpot.")
            else:
                raise e

    def parse_response_error_message(self, response: requests.Response) -> Optional[str]:
        try:
            body = response.json()
        except json.decoder.JSONDecodeError:
            return response.text
        if body.get("category") == "MISSING_SCOPES":
            if "errors" in body:
                errors = body["errors"]
                if len(errors) > 0:
                    error = errors[0]
                    missing_scopes = error.get("context", {}).get("requiredScopes")
                    return f"Invalid permissions for {self.name}. Please ensure the all scopes are authorized for. Missing scopes {missing_scopes}"
        return super().parse_response_error_message(response)

    @staticmethod
    def _convert_datetime_to_string(dt: pendulum.datetime, declared_format: str = None) -> str:
        if declared_format == "date":
            return dt.to_date_string()
        elif declared_format == "date-time":
            return dt.to_rfc3339_string()

    @classmethod
    def _cast_datetime(cls, field_name: str, field_value: Any, declared_format: str = None) -> Any:
        """
        If format is date/date-time, but actual value is timestamp, convert timestamp to date/date-time string.
        """
        if not field_value:
            return field_value

        try:
            dt = pendulum.parse(field_value)
            return cls._convert_datetime_to_string(dt, declared_format=declared_format)
        except (ValueError, TypeError) as ex:
            logger.warning(
                f"Couldn't parse date/datetime string in {field_name}, trying to parse timestamp... Field value: {field_value}. Ex: {ex}"
            )

        try:
            dt = pendulum.from_timestamp(int(field_value) / 1000)
            return cls._convert_datetime_to_string(dt, declared_format=declared_format)
        except (ValueError, TypeError) as ex:
            logger.warning(f"Couldn't parse timestamp in {field_name}. Field value: {field_value}. Ex: {ex}")

        return field_value

    @classmethod
    def _cast_value(cls, declared_field_types: List, field_name: str, field_value: Any, declared_format: str = None) -> Any:
        """
        Convert record's received value according to its declared catalog json schema type / format / attribute name.
        :param declared_field_types type from catalog schema
        :param field_name value's attribute name
        :param field_value actual value to cast
        :param declared_format format field value from catalog schema
        :return Converted value for record
        """

        if "null" in declared_field_types:
            if field_value is None:
                return field_value
            # Sometime hubspot output empty string on field with format set.
            # Set it to null to avoid errors on destination' normalization stage.
            if declared_format and field_value == "":
                return None

        if declared_format in ["date", "date-time"]:
            field_value = cls._cast_datetime(field_name, field_value, declared_format=declared_format)

        actual_field_type = type(field_value)
        actual_field_type_name = CUSTOM_FIELD_TYPE_TO_VALUE.get(actual_field_type)
        if actual_field_type_name in declared_field_types:
            return field_value

        target_type_name = next(filter(lambda t: t != "null", declared_field_types))
        target_type = CUSTOM_FIELD_VALUE_TO_TYPE.get(target_type_name)

        if target_type_name == "boolean" and actual_field_type_name == "string":
            # do not cast string with bool function to prevent : bool("false") = True
            if str(field_value).lower() in ["true", "false"]:
                field_value = str(field_value).lower() == "true"
                return field_value

        if target_type_name == "number":
            # do not cast numeric IDs into float, use integer instead
            target_type = int if field_value.isnumeric() else target_type
            field_value = field_value.replace(",", "")

        if target_type_name != "string" and field_value == "":
            # do not cast empty strings, return None instead to be properly casted.
            field_value = None
            return field_value

        try:
            casted_value = target_type(field_value)
        except ValueError:
            logger.exception(f"Could not cast in stream `{cls.__name__}` `{field_name}` {field_value=} to `{target_type}`")
            return field_value

        return casted_value

    def _cast_record(
        self,
        record: Mapping,
        properties: Mapping[str, Any] = None,
        properties_key: str = None,
        logging_message: str = "",
        field_validation: Callable = None,
    ):
        """
        Cast record fields by provided properties schema.
        They can be either fields in record root or in properties key provided.
        :param record: record to cast

        :param properties: properties schema to cast record by
        :param properties_key: key in record where properties are stored
        :param logging_message: message to log when field is discarded
        :param field_validation: function to validate field before casting
        :return: record
        """

        def get_record_items():
            if properties_key:
                return record[properties_key].items()
            return record.items()

        for field_name, field_value in get_record_items():
            if field_validation and not field_validation(field_name, field_value):
                continue
            if field_name not in properties:
                self.logger.info("{}: record id:{}, property_value: {}".format(logging_message, record.get("id"), field_name))
                continue
            declared_field_types = properties[field_name].get("type", [])
            if not isinstance(declared_field_types, Iterable):
                declared_field_types = [declared_field_types]
            declared_format = properties[field_name].get("format")
            record_to_cast = record[properties_key] if properties_key else record
            record_to_cast[field_name] = self._cast_value(
                declared_field_types=declared_field_types, field_name=field_name, field_value=field_value, declared_format=declared_format
            )
        return record

    def _cast_record_fields_if_needed(self, record: Mapping, properties: Mapping[str, Any] = None) -> Mapping:
        """
        Cast fields in properties key in record to the Schema returned by "/properties/v2/{self.entity}/properties" endpoint.
        Properties request (self.properties) is cached, so it is not called for each record.
        """
        if not self.entity or not record.get("properties"):
            return record

        properties = properties or self.properties

        return self._cast_record(
            record=record,
            properties=properties,
            logging_message="Property discarded: not matching with properties schema",
            properties_key="properties",
        )

    def _cast_record_fields_with_schema_if_needed(self, record: Mapping) -> Mapping:
        """
        Cast specific record items from the response to the JSON Schema type.
        We've found hubspot changing types and not properly documented, then we cast to expected schema.
        For now, we just cast specific fields.
        """
        if not self.cast_fields:
            return record

        properties = self.get_json_schema().get("properties")

        def field_validation(field_name: str, field_value: Any):
            # properties fields is cast by _cast_record_fields_if_needed
            return field_name in self.cast_fields and field_name != "properties"

        return self._cast_record(
            record=record,
            properties=properties,
            logging_message="Property discarded: not matching with stream schema",
            field_validation=field_validation,
        )

    def _transform(self, records: Iterable) -> Iterable:
        """Preprocess record before emitting"""
        for record in records:
            record = self._cast_record_fields_if_needed(record)
            record = self._cast_record_fields_with_schema_if_needed(record)
            if self.created_at_field and self.updated_at_field and record.get(self.updated_at_field) is None:
                record[self.updated_at_field] = record[self.created_at_field]
            if self._transformations:
                for transformation in self._transformations:
                    transformation.transform(record_or_schema=record)
            yield record

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = pendulum.parse(value)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value

    def _filter_old_records(self, records: Iterable) -> Iterable:
        """Skip records that was updated before our start_date"""
        for record in records:
            updated_at = record[self.updated_at_field]
            if updated_at:
                updated_at = self._field_to_datetime(updated_at)
                if updated_at < self._start_date:
                    continue
            yield record

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        default_params = {self.limit_field: self.limit}
        params = {**default_params}
        if next_page_token:
            params.update(next_page_token)
        return params

    def _parse_response(self, response: requests.Response):
        return self._api._parse_and_handle_errors(response)

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        response = self._parse_response(response)

        if isinstance(response, Mapping):
            if response.get("status", None) == "error":
                """
                When the API Key doen't have the permissions to access the endpoint,
                we break the read, skip this stream and log warning message for the user.

                Example:

                response.json() = {
                    'status': 'error',
                    'message': 'This hapikey (....) does not have proper permissions! (requires any of [automation-access])',
                    'correlationId': '111111-2222-3333-4444-55555555555'}
                """
                self.logger.warning(f"Stream `{self.name}` cannot be procced. {response.get('message')}")
                return

            if response.get(self.data_field) is None:
                """
                When the response doen't have the stream's data, raise an exception.
                """
                raise RuntimeError("Unexpected API response: {} not in {}".format(self.data_field, response.keys()))

            yield from response[self.data_field]

        else:
            response = list(response)
            yield from response

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response = self._parse_response(response)

        if isinstance(response, Mapping):
            if "paging" in response:  # APIv3 pagination
                if "next" in response["paging"]:
                    return {"after": response["paging"]["next"]["after"]}
            else:
                if self.more_key:
                    if not response.get(self.more_key, False):
                        return
                    if self.page_field in response:
                        return {self.page_filter: response[self.page_field]}
                if self.page_field in response and response[self.page_filter] + self.limit < response.get("total"):
                    return {self.page_filter: response[self.page_filter] + self.limit}
        else:
            if len(response) >= self.limit:
                self.offset += self.limit
                return {self.page_filter: self.offset}

    @staticmethod
    def _get_field_props(field_type: str) -> Mapping[str, List[str]]:
        if field_type in VALID_JSON_SCHEMA_TYPES:
            return {
                "type": ["null", field_type],
            }

        converted_type, field_format = KNOWN_CONVERTIBLE_SCHEMA_TYPES.get(field_type) or (None, None)

        if not converted_type:
            converted_type = "string"
            logger.warning(f"Unsupported type {field_type} found")

        field_props = {
            "type": ["null", converted_type or field_type],
        }

        if field_format:
            field_props["format"] = field_format

        return field_props

    @property
    @lru_cache()
    def properties(self) -> Mapping[str, Any]:
        """Some entities have dynamic set of properties, so we're trying to resolve those at runtime"""
        props = {}
        if not self.entity:
            return props
        if not self.properties_scope_is_granted():
            logger.warning(
                f"Check your API key has the following permissions granted: {self.properties_scopes}, "
                f"to be able to fetch all properties available."
            )
            return props
        data, response = self._api.get(f"/properties/v2/{self.entity}/properties")
        for row in data:
            props[row["name"]] = self._get_field_props(row["type"])

        if self._transformations:
            for transformation in self._transformations:
                transformation.transform(record_or_schema=props)

        return props

    def properties_scope_is_granted(self):
        return not self.properties_scopes - self.granted_scopes if self.properties_scopes and self.granted_scopes else True

    def _flat_associations(self, records: Iterable[MutableMapping]) -> Iterable[MutableMapping]:
        """When result has associations we prefer to have it flat, so we transform this:

        "associations": {
            "contacts": {
                "results": [{"id": "201", "type": "company_to_contact"}, {"id": "251", "type": "company_to_contact"}]}
            }
        }

        to this:

        "contacts": [201, 251]
        """
        for record in records:
            if "associations" in record:
                associations = record.pop("associations")
                for name, association in associations.items():
                    record[name.replace(" ", "_")] = [row["id"] for row in association.get("results", [])]
            yield record

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return HubspotAvailabilityStrategy()


class ClientSideIncrementalStream(Stream, CheckpointMixin):
    _cursor_value = ""

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self.updated_at_field

    @property
    @abstractmethod
    def updated_at_field(self):
        """Name of the field associated with the state"""

    @property
    @abstractmethod
    def cursor_field_datetime_format(self):
        """Date-time expressed in pendulum formats, see: https://pendulum.eustace.io/docs/#formatter"""

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, "")

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> bool:
        """
        Filter out old records that come from source in unsorted order.
        Hubspot API uses 2 date-time formats for different endpoints:
        1. "YYYY-MM-DDTHH:mm:ss.SSSSSSZ" - date-time in ISO format
        2. "x" - date-time in timestamp in milliseconds
        """
        int_field_type = "integer" in self.get_json_schema().get("properties").get(self.cursor_field).get("type")
        record_value = (
            pendulum.parse(record.get(self.cursor_field))
            if isinstance(record.get(self.cursor_field), str)
            else pendulum.from_format(str(record.get(self.cursor_field)), self.cursor_field_datetime_format)
        )
        # default state value before all futher checks
        state_value = self._start_date
        # we should check the presence of `stream_state` to overcome `availability strategy` check issues
        if stream_state:
            state_value = stream_state.get(self.cursor_field)
            # sometimes the state is saved as `EMPTY STRING` explicitly
            state_value = (
                self._start_date if str(state_value) == "" else pendulum.from_format(str(state_value), self.cursor_field_datetime_format)
            )
        # compare the state with record values and get the max value between of two
        cursor_value = max(state_value, record_value)
        max_state = max(str(self.state.get(self.cursor_field)), cursor_value.format(self.cursor_field_datetime_format))
        # save the state
        self.state = {self.cursor_field: int(max_state) if int_field_type else max_state}
        # emmit record if it has bigger cursor value compare to the state (`True` only)
        return record_value >= state_value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self.filter_by_state(stream_state=stream_state, record=record):
                yield record


class AssociationsStream(Stream):
    """
    Designed to read associations of CRM objects during incremental syncs, since Search API does not support
    retrieving associations.
    """

    http_method = "POST"
    filter_old_records = False

    def __init__(self, parent_stream: Stream, identifiers: Iterable[Union[int, str]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_stream = parent_stream
        self.identifiers = identifiers

    @property
    def url(self):
        """
        although it is not used, it needs to be implemented because it is an abstract property
        """
        return ""

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> str:
        return f"/crm/v4/associations/{self.parent_stream.entity}/{stream_slice}/batch/read"

    def scopes(self) -> Set[str]:
        return self.parent_stream.scopes

    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[str]:
        return self.parent_stream.associations

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {"inputs": [{"id": str(id_)} for id_ in self.identifiers]}


class IncrementalStream(Stream, ABC):
    """Stream that supports state and incremental read"""

    state_pk = "timestamp"
    limit = 1000
    # Flag which enable/disable chunked read in read_chunked method
    # False -> chunk size is max (only one slice), True -> chunk_size is 30 days
    need_chunk = True
    state_checkpoint_interval = 500
    last_slice = None

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self.updated_at_field

    @property
    @abstractmethod
    def updated_at_field(self):
        """Name of the field associated with the state"""

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
        latest_cursor = None
        for record in records:
            cursor = self._field_to_datetime(record[self.updated_at_field])
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record

        is_last_slice = False
        if self.last_slice:
            is_last_slice = stream_slice == self.last_slice
        self._update_state(latest_cursor=latest_cursor, is_last_record=is_last_slice)

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self._sync_mode is None:
            raise RuntimeError("sync_mode is not defined")
        if self._state:
            if self.state_pk == "timestamp":
                return {self.cursor_field: int(self._state.timestamp() * 1000)}
            return {self.cursor_field: self._state.to_iso8601_string()}
        return {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if value.get(self.cursor_field):
            self._state = self._field_to_datetime(value[self.cursor_field])

    def set_sync(self, sync_mode: SyncMode):
        self._sync_mode = sync_mode
        if self._sync_mode == SyncMode.incremental:
            if not self._state:
                self._state = self._start_date
            self._state = self._start_date = max(self._state, self._start_date)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None
        self._sync_mode = None
        self._init_sync = pendulum.now("utc")

    def _update_state(self, latest_cursor, is_last_record=False):
        """
        The first run uses an endpoint that is not sorted by updated_at but is
        sorted by id because of this instead of updating the state by reading
        the latest cursor the state will set it at the end with the time the synch
        started. With the proposed `state strategy`, it would capture all possible
        updated entities in incremental synch.
        """
        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state
        if is_last_record:
            self._state = self._init_sync

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.set_sync(sync_mode)
        chunk_size = pendulum.duration(days=30)
        slices = []

        now_ts = int(pendulum.now().timestamp() * 1000)
        start_ts = int(self._start_date.timestamp() * 1000)
        max_delta = now_ts - start_ts
        chunk_size = int(chunk_size.total_seconds() * 1000) if self.need_chunk else max_delta

        for ts in range(start_ts, now_ts, chunk_size):
            end_ts = ts + chunk_size
            slices.append(
                {
                    "startTimestamp": ts,
                    "endTimestamp": end_ts,
                }
            )
        # Save the last slice to ensure we save the lastest state as the initial sync date
        if len(slices) > 0:
            self.last_slice = slices[-1]

        return slices

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if stream_slice:
            params.update(stream_slice)
        return params


class CRMSearchStream(IncrementalStream, ABC):
    limit = 100  # This value is used only when state is None.
    state_pk = "updatedAt"
    updated_at_field = "updatedAt"
    last_modified_field: str = None
    associations: List[str] = []
    fully_qualified_name: str = None

    # added to guarantee the data types, declared for the stream's schema
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def url(self):
        object_type_id = self.fully_qualified_name or self.entity
        return f"/crm/v3/objects/{object_type_id}/search" if self.state else f"/crm/v3/objects/{object_type_id}"

    def __init__(
        self,
        include_archived_only: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._state = None
        self._include_archived_only = include_archived_only

    @retry_connection_handler(max_tries=5, factor=5)
    @retry_after_handler(fixed_retry_after=1, max_tries=3)
    def search(
        self, url: str, data: Mapping[str, Any], params: MutableMapping[str, Any] = None
    ) -> Tuple[Union[Mapping[str, Any], List[Mapping[str, Any]]], requests.Response]:
        # We can safely retry this POST call, because it's a search operation.
        # Given Hubspot does not return any Retry-After header (https://developers.hubspot.com/docs/api/crm/search)
        # from the search endpoint, it waits one second after trying again.
        # As per their docs: `These search endpoints are rate limited to four requests per second per authentication token`.
        return self._api.post(url=url, data=data, params=params)

    def _process_search(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        last_id=None,
    ) -> Tuple[List, requests.Response]:
        stream_records = {}
        properties_list = list(self.properties.keys())
        if last_id == None:
            last_id = 0
        # The search query below uses the following criteria:
        #   - Last modified >= timestemp of previous sync
        #   - Last modified <= timestamp of current sync to avoid open ended queries
        #   - Object primary key <= last_id with initial value 0, then max(last_id) returned from previous pagination loop
        #   - Sort results by primary key ASC
        # Note: Although results return out of chronological order, sorting on primary key ensures retrieval of *all* records
        #     once the final pagination loop completes. This is preferable to sorting by a non-unique value, such as
        #     last modified date, which may result in an infinite loop in some edge cases.
        key = self.primary_key
        if key == "id":
            key = "hs_object_id"
        payload = (
            {
                "filters": [
                    {"value": int(self._state.timestamp() * 1000), "propertyName": self.last_modified_field, "operator": "GTE"},
                    {"value": int(self._init_sync.timestamp() * 1000), "propertyName": self.last_modified_field, "operator": "LTE"},
                    {"value": last_id, "propertyName": key, "operator": "GTE"},
                ],
                "sorts": [{"propertyName": key, "direction": "ASCENDING"}],
                "properties": properties_list,
                "limit": 100,
            }
            if self.state
            else {}
        )
        if next_page_token:
            payload.update(next_page_token["payload"])

        response, raw_response = self.search(url=self.url, data=payload)
        for record in self._transform(self.parse_response(raw_response, stream_state=stream_state, stream_slice=stream_slice)):
            stream_records[record["id"]] = record

        return list(stream_records.values()), raw_response

    def _read_associations(self, records: Iterable) -> Iterable[Mapping[str, Any]]:
        records_by_pk = {record[self.primary_key]: record for record in records}
        identifiers = list(map(lambda x: x[self.primary_key], records))
        associations_stream = AssociationsStream(
            api=self._api, start_date=self._start_date, credentials=self._credentials, parent_stream=self, identifiers=identifiers
        )
        slices = associations_stream.stream_slices(sync_mode=SyncMode.full_refresh)

        for _slice in slices:
            logger.info(f"Reading {_slice} associations of {self.entity}")
            associations = associations_stream.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
            for group in associations:
                current_record = records_by_pk[group["from"]["id"]]
                associations_list = current_record.get(_slice, [])
                associations_list.extend(association["toObjectId"] for association in group["to"])
                current_record[_slice] = associations_list
        return records_by_pk.values()

    def get_max(self, val1, val2):
        try:
            # Try to convert both values to integers
            int_val1 = int(val1)
            int_val2 = int(val2)
            return max(int_val1, int_val2)
        except ValueError:
            # If conversion fails, fall back to string comparison
            return max(str(val1), str(val2))

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        last_id = None
        max_last_id = None

        while not pagination_complete:
            if self.state:
                records, raw_response = self._process_search(
                    next_page_token=next_page_token, stream_state=stream_state, stream_slice=stream_slice, last_id=max_last_id
                )
                if self.associations:
                    records = self._read_associations(records)
            else:
                records, raw_response = self._read_stream_records(
                    stream_slice=stream_slice,
                    stream_state=stream_state,
                    next_page_token=next_page_token,
                )
                records = self._flat_associations(records)
            records = self._filter_old_records(records)
            records = self.record_unnester.unnest(records)

            for record in records:
                last_id = self.get_max(record[self.primary_key], last_id) if last_id else record[self.primary_key]
                yield record

            next_page_token = self.next_page_token(raw_response)
            if not next_page_token:
                pagination_complete = True
            elif self.state and next_page_token["payload"]["after"] >= 10000:
                # Hubspot documentation states that the search endpoints are limited to 10,000 total results
                # for any given query. Attempting to page beyond 10,000 will result in a 400 error.
                # https://developers.hubspot.com/docs/api/crm/search. We stop getting data at 10,000 and
                # start a new search query with the latest id that has been collected.
                max_last_id = self.get_max(max_last_id, last_id) if max_last_id else last_id
                next_page_token = None

        # Since Search stream does not have slices is safe to save the latest
        # state as the initial sync date
        self._update_state(latest_cursor=self._init_sync, is_last_record=True)
        # Always return an empty generator just in case no records were ever yielded
        yield from []

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"archived": str(self._include_archived_only).lower(), "associations": self.associations, "limit": self.limit}
        if next_page_token:
            params.update(next_page_token.get("params", {}))
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response = self._parse_response(response)
        params = {}
        payload = {}

        if "paging" in response and "next" in response["paging"] and "after" in response["paging"]["next"]:
            params["after"] = int(response["paging"]["next"]["after"])
            payload["after"] = int(response["paging"]["next"]["after"])

            return {"params": params, "payload": payload}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.set_sync(sync_mode, stream_state)
        return [{}]  # I changed this from [None] since this is a more accurate depiction of what is actually being done. Sync one slice

    def set_sync(self, sync_mode: SyncMode, stream_state):
        self._sync_mode = sync_mode
        if self._sync_mode == SyncMode.incremental:
            if stream_state:
                if not self._state:
                    self._state = self._start_date
                else:
                    self._state = self._start_date = max(self._state, self._start_date)


class CRMObjectStream(Stream):
    """Unified stream interface for CRM objects.
    You need to provide `entity` parameter to read concrete stream, possible values are:
        company, contact, deal, line_item, owner, product, ticket, quote
    You can also include associated records (IDs), provide associations parameter - a list of entity names:
        contacts, tickets, deals, engagements
    see https://developers.hubspot.com/docs/api/crm/understanding-the-crm for more details
    """

    entity: Optional[str] = None
    associations: List[str] = []
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"

    @property
    def url(self):
        """Entity URL"""
        return f"/crm/v3/objects/{self.entity}"

    def __init__(self, include_archived_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._include_archived_only = include_archived_only

        if not self.entity:
            raise ValueError("Entity must be set either on class or instance level")


class CRMObjectIncrementalStream(CRMObjectStream, IncrementalStream):
    state_pk = "updatedAt"
    limit = 100
    need_chunk = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = IncrementalStream.request_params(
            self, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )
        params.update(
            {
                "archived": str(self._include_archived_only).lower(),
                "associations": self.associations,
            }
        )
        return params

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        records = IncrementalStream.read_records(
            self,
            sync_mode,
            cursor_field=cursor_field,
            stream_slice=stream_slice,
            stream_state=stream_state,
        )
        yield from self._flat_associations(records)


class Campaigns(ClientSideIncrementalStream):
    """Email campaigns, API v1
    There is some confusion between emails and campaigns in docs, this endpoint returns actual emails
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_campaign_data
    """

    url = "/email/public/v1/campaigns"
    more_key = "hasMore"
    data_field = "campaigns"
    limit = 500
    updated_at_field = "lastUpdatedTime"
    cursor_field_datetime_format = "x"
    primary_key = "id"
    scopes = {"crm.lists.read"}
    unnest_fields = ["counters"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for row in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            record, response = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            if self.filter_by_state(stream_state=stream_state, record=row):
                yield from self.record_unnester.unnest([{**row, **record}])


class ContactLists(IncrementalStream):
    """Contact lists, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/lists/get_lists
    """

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    url = "/contacts/v1/lists"
    data_field = "lists"
    more_key = "has-more"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    limit_field = "count"
    primary_key = "listId"
    need_chunk = False
    scopes = {"crm.lists.read"}
    unnest_fields = ["metaData"]


# class ContactsAllBase(ClientSideIncrementalStream):
class ContactsAllBase(Stream):
    url = "/contacts/v1/lists/all/contacts/all"
    updated_at_field = "timestamp"
    more_key = "has-more"
    data_field = "contacts"
    page_filter = "vidOffset"
    page_field = "vid-offset"
    primary_key = "canonical-vid"
    limit_field = "count"
    scopes = {"crm.objects.contacts.read"}
    properties_scopes = {"crm.schemas.contacts.read"}
    records_field = None
    filter_field = None
    filter_value = None
    _state = {}
    limit_field = "count"
    limit = 100

    def _transform(self, records: Iterable) -> Iterable:
        for record in super()._transform(records):
            canonical_vid = record.get("canonical-vid")
            for item in record.get(self.records_field, []):
                yield {"canonical-vid": canonical_vid, **item}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.filter_field and self.filter_value:
            params.update({self.filter_field: self.filter_value})
        return params


class ResumableFullRefreshMixin(Stream, CheckpointMixin, ABC):
    checkpoint_by_page = True

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This is a specialized read_records for resumable full refresh that only attempts to read a single page of records
        at a time and updates the state w/ a synthetic cursor based on the Hubspot cursor pagination value `vidOffset`
        """

        next_page_token = stream_slice
        yield from self.read_paged_records(next_page_token=next_page_token, stream_slice=stream_slice, stream_state=stream_state)


class ContactsListMemberships(ContactsAllBase, ClientSideIncrementalStream):
    """Contacts list Memberships, API v1
    The Stream was created due to issue #8477, where supporting List Memberships in Contacts stream was requested.
    According to the issue this feature is supported in API v1 by setting parameter showListMemberships=true
    in get all contacts endpoint. API will return list memberships for each contact record.
    But for syncing Contacts API v3 is used, where list memberships for contacts isn't supported.
    Therefore, new stream was created based on get all contacts endpoint of API V1.
    Docs: https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts
    """

    records_field = "list-memberships"
    filter_field = "showListMemberships"
    filter_value = True
    checkpoint_by_page = False

    @property
    def updated_at_field(self) -> str:
        """Name of the field associated with the state"""
        return "timestamp"

    @property
    def cursor_field_datetime_format(self) -> str:
        """Cursor value expected to be a timestamp in milliseconds"""
        return "x"


class ContactsFormSubmissions(ContactsAllBase, ResumableFullRefreshMixin, ABC):
    records_field = "form-submissions"
    filter_field = "formSubmissionMode"
    filter_value = "all"


class ContactsMergedAudit(ContactsAllBase, ResumableFullRefreshMixin, ABC):
    records_field = "merge-audits"
    unnest_fields = ["merged_from_email", "merged_to_email"]


class Deals(CRMSearchStream):
    """Deals, API v3"""

    entity = "deal"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "companies", "line_items"]
    primary_key = "id"
    scopes = {"contacts", "crm.objects.deals.read"}
    _transformations = [NewtoLegacyFieldTransformation(field_mapping=DEALS_NEW_TO_LEGACY_FIELDS_MAPPING)]


class DealsArchived(ClientSideIncrementalStream):
    """Archived Deals, API v3"""

    url = "/crm/v3/objects/deals"
    entity = "deal"
    updated_at_field = "archivedAt"
    created_at_field = "createdAt"
    associations = ["contacts", "companies", "line_items"]
    cursor_field_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
    primary_key = "id"
    scopes = {"contacts", "crm.objects.deals.read"}
    _transformations = [NewtoLegacyFieldTransformation(field_mapping=DEALS_NEW_TO_LEGACY_FIELDS_MAPPING)]

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({"archived": "true", "associations": self.associations})
        return params


class DealPipelines(ClientSideIncrementalStream):
    """Deal pipelines, API v1,
    This endpoint requires the contacts scope the tickets scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """

    url = "/crm-pipelines/v1/pipelines/deals"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    cursor_field_datetime_format = "x"
    primary_key = "pipelineId"
    scopes = {"crm.objects.contacts.read"}


class DealSplits(CRMSearchStream):
    """Deal splits, API v3"""

    entity = "deal_split"
    last_modified_field = "hs_lastmodifieddate"
    primary_key = "id"
    scopes = {"crm.objects.deals.read"}


class TicketPipelines(ClientSideIncrementalStream):
    """Ticket pipelines, API v1
    This endpoint requires the tickets scope.
    Docs: https://developers.hubspot.com/docs/api/crm/pipelines
    """

    url = "/crm/v3/pipelines/tickets"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    cursor_field_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
    primary_key = "id"
    scopes = {
        "media_bridge.read",
        "tickets",
        "crm.schemas.custom.read",
        "e-commerce",
        "timeline",
        "contacts",
        "crm.schemas.contacts.read",
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.deals.read",
        "crm.schemas.quotes.read",
        "crm.objects.deals.write",
        "crm.objects.companies.read",
        "crm.schemas.companies.read",
        "crm.schemas.deals.read",
        "crm.schemas.line_items.read",
        "crm.objects.companies.write",
    }


class EmailEvents(IncrementalStream):
    """Email events, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_events
    """

    url = "/email/public/v1/events"
    data_field = "events"
    more_key = "hasMore"
    updated_at_field = "created"
    created_at_field = "created"
    primary_key = "id"
    scopes = {"content"}


class EngagementsABC(Stream, ABC):
    more_key = "hasMore"
    updated_at_field = "lastUpdated"
    created_at_field = "createdAt"
    primary_key = "id"
    scopes = {"crm.objects.companies.read", "crm.objects.contacts.read", "crm.objects.deals.read", "tickets", "e-commerce"}

    def _transform(self, records: Iterable) -> Iterable:
        yield from super()._transform({**record.pop("engagement"), **record} for record in records)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"count": 250}
        if next_page_token:
            params["offset"] = next_page_token["offset"]
        return params


class EngagementsAll(EngagementsABC):
    """All Engagements API:
    https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements

    Note: Returns all engagements records ordered by 'createdAt' (not 'lastUpdated') field
    """

    unnest_fields = ["associations", "metadata"]

    @property
    def url(self):
        return "/engagements/v1/engagements/paged"


class EngagementsRecentError(Exception):
    pass


class EngagementsRecent(EngagementsABC):
    """Recent Engagements API:
    https://legacydocs.hubspot.com/docs/methods/engagements/get-recent-engagements

    Get the most recently created or updated engagements in a portal, sorted by when they were last updated,
    with the most recently updated engagements first.

    Important: This endpoint returns only last 10k most recently updated records in the last 30 days.
    """

    total_records_limit = 10000
    last_days_limit = 29
    unnest_fields = ["associations", "metadata"]

    @property
    def url(self):
        return "/engagements/v1/engagements/recent/modified"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._start_date < pendulum.now() - timedelta(days=self.last_days_limit):
            raise EngagementsRecentError(
                '"Recent engagements" API returns records updated in the last 30 days only. '
                f'Start date {self._start_date} is older so "All engagements" API should be used'
            )

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                "since": int(self._start_date.timestamp() * 1000),
                "count": 100,
            }
        )
        return params

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # Check if "Recent engagements" API is applicable for use
        response_info = response.json()
        if response_info:
            total = response_info.get("total")
            if total > self.total_records_limit:
                yield from []
                raise EngagementsRecentError(
                    '"Recent engagements" API returns only 10k most recently updated records. '
                    'API response indicates that there are more records so "All engagements" API should be used'
                )
        yield from super().parse_response(response, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)


class Engagements(EngagementsABC, IncrementalStream):
    """Engagements stream does not send requests directly, instead it uses:
    - EngagementsRecent if start_date/state is less than 30 days and API is able to return all records (<10k), or
    - EngagementsAll which extracts all records, but supports filter on connector side
    """

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def url(self):
        return "/engagements/v1/engagements/paged"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.set_sync(sync_mode)
        return [None]

    def process_records(self, records: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
        """Process each record to find latest cursor value"""
        for record in records:
            cursor = self._field_to_datetime(record[self.updated_at_field])
            self.latest_cursor = max(cursor, self.latest_cursor) if self.latest_cursor else cursor
            yield record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.latest_cursor = None

        # The date we need records since
        since_date = self._start_date
        if stream_state:
            since_date_timestamp = stream_state.get(self.updated_at_field)
            if since_date_timestamp:
                since_date = pendulum.from_timestamp(int(since_date_timestamp) / 1000)

        stream_params = {
            "api": self._api,
            "start_date": since_date,
            "credentials": self._credentials,
            "acceptance_test_config": {casing.camel_to_snake(EngagementsRecent.__name__): self._acceptance_test_config},
        }

        try:
            # Try 'Recent' API first, since it is more efficient
            records = EngagementsRecent(**stream_params).read_records(sync_mode.full_refresh, cursor_field)
            yield from self.process_records(records)
        except EngagementsRecentError as e:
            # if 'Recent' API in not applicable and raises the error
            # then use 'All' API which returns all records, which are filtered on connector side
            self.logger.info(e)
            records = EngagementsAll(**stream_params).read_records(sync_mode.full_refresh, cursor_field)
            yield from self.process_records(records)

        # State should be updated only once at the end of the sync
        # because records are not ordered in ascending by 'lastUpdated' field
        self._update_state(latest_cursor=self.latest_cursor, is_last_record=True)

    def _transform(self, records: Iterable) -> Iterable:
        # transformation is not needed, because it was done in a substream
        yield from records


class Forms(ClientSideIncrementalStream):
    """Marketing Forms, API v3
    by default non-marketing forms are filtered out of this endpoint
    Docs: https://developers.hubspot.com/docs/api/marketing/forms
    """

    entity = "form"
    url = "/marketing/v3/forms"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    cursor_field_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
    primary_key = "id"
    scopes = {"forms"}


class FormSubmissions(ClientSideIncrementalStream):
    """Marketing Forms, API v1
    This endpoint requires the forms scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form
    """

    url = "/form-integrations/v1/submissions/forms"
    limit = 50
    updated_at_field = "updatedAt"
    cursor_field_datetime_format = "x"
    scopes = {"forms"}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> str:
        return f"{self.url}/{stream_slice['form_id']}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forms = Forms(**kwargs)

    def _transform(self, records: Iterable) -> Iterable:
        for record in super()._transform(records):
            keys = record.keys()

            # There's no updatedAt field in the submission however forms fetched by using this field,
            # so it has to be added to the submissions otherwise it would fail when calling _filter_old_records
            if "updatedAt" not in keys:
                record["updatedAt"] = record["submittedAt"]

            yield record

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = []
        seen = set()
        # To get submissions for all forms date filtering has to be disabled
        self.forms.filter_old_records = False
        for form in self.forms.read_records(sync_mode):
            if form["id"] not in seen:
                seen.add(form["id"])
                slices.append({"form_id": form["id"]})
        return slices

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            if self.filter_by_state(stream_state=stream_state, record=record):
                record["formId"] = stream_slice["form_id"]
                yield record


class MarketingEmails(Stream):
    """Marketing Email, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-emails
    """

    url = "/marketing-emails/v1/emails/with-statistics"
    data_field = "objects"
    limit = 250
    page_field = "limit"
    updated_at_field = "updated"
    created_at_field = "created"
    primary_key = "id"
    scopes = {"content"}
    cast_fields = ["rootMicId"]


class Owners(ClientSideIncrementalStream):
    """Owners, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/owners/get_owners
    """

    url = "/crm/v3/owners"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    cursor_field_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
    primary_key = "id"
    scopes = {"crm.objects.owners.read"}


class OwnersArchived(ClientSideIncrementalStream):
    """Archived Owners, API v3"""

    url = "/crm/v3/owners"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    cursor_field_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSSSSZ"
    primary_key = "id"
    scopes = {"crm.objects.owners.read"}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["archived"] = "true"
        return params


class PropertyHistory(ClientSideIncrementalStream):
    """Contacts Endpoint, API v1
    Is used to get all Contacts and the history of their respective
    Properties. Whenever a property is changed it is added here.
    Docs: https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts
    """

    updated_at_field = "timestamp"
    created_at_field = "timestamp"
    denormalize_records = True
    limit = 100

    @property
    @abstractmethod
    def page_field(self) -> str:
        """Page offset field"""

    @property
    @abstractmethod
    def limit_field(self) -> str:
        """Limit query field"""

    @property
    @abstractmethod
    def page_filter(self) -> str:
        """Query param name that indicates page offset"""

    @property
    @abstractmethod
    def more_key(self) -> str:
        """Field that indicates that are more records"""

    @property
    @abstractmethod
    def scopes(self) -> set:
        """Scopes needed to get access to CRM object"""

    @property
    @abstractmethod
    def properties_scopes(self) -> set:
        """Scopes needed to get access to CRM object properies"""

    @property
    @abstractmethod
    def entity(self) -> str:
        """
        CRM object entity name.
        This is usually a part of some URL or key that contains data in response
        """

    @property
    @abstractmethod
    def primary_key(self) -> str:
        """Indicates a field name which is considered to be a primary key of the stream"""

    @property
    @abstractmethod
    def entity_primary_key(self) -> str:
        """Indicates a field name which is considered to be a primary key of the parent entity"""

    @property
    @abstractmethod
    def additional_keys(self) -> list:
        """The root keys to be placed into each record while iterating through versions"""

    @property
    @abstractmethod
    def last_modified_date_field_name(self) -> str:
        """Last modified date field name"""

    @property
    @abstractmethod
    def data_field(self) -> str:
        """A key that contains data in response"""

    @property
    @abstractmethod
    def url(self) -> str:
        """An API url"""

    @property
    def cursor_field_datetime_format(self) -> str:
        """Cursor value expected to be a timestamp in milliseconds"""
        return "x"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {self.limit_field: self.limit, "propertyMode": "value_and_history"}
        if next_page_token:
            params.update(next_page_token)
        return params

    def _transform(self, records: Iterable) -> Iterable:
        for record in records:
            properties = record.get("properties")
            primary_key = record.get(self.entity_primary_key)
            additional_keys = {additional_key: record.get(additional_key) for additional_key in self.additional_keys}
            value_dict: Dict
            for property_name, value_dict in properties.items():
                versions = value_dict.get("versions")
                if property_name == self.last_modified_date_field_name:
                    # Skipping the lastmodifieddate since it only returns the value
                    # when one field of a contact was changed no matter which
                    # field was changed. It therefore creates overhead, since for
                    # every changed property there will be the date it was changed in itself
                    # and a change in the lastmodifieddate field.
                    continue
                if versions:
                    for version in versions:
                        version["property"] = property_name
                        version[self.entity_primary_key] = primary_key
                        yield version | additional_keys


class ContactsPropertyHistory(PropertyHistory):
    @property
    def scopes(self):
        return {"crm.objects.contacts.read"}

    @property
    def properties_scopes(self):
        return {"crm.schemas.contacts.read"}

    @property
    def page_field(self) -> str:
        return "vid-offset"

    @property
    def limit_field(self) -> str:
        return "count"

    @property
    def page_filter(self) -> str:
        return "vidOffset"

    @property
    def more_key(self) -> str:
        return "has-more"

    @property
    def entity(self):
        return "contacts"

    @property
    def entity_primary_key(self) -> list:
        return "vid"

    @property
    def primary_key(self) -> list:
        return ["vid", "property", "timestamp"]

    @property
    def additional_keys(self) -> list:
        return ["portal-id", "is-contact", "canonical-vid"]

    @property
    def last_modified_date_field_name(self):
        return "lastmodifieddate"

    @property
    def data_field(self):
        return "contacts"

    @property
    def url(self):
        return "/contacts/v1/lists/all/contacts/all"


class PropertyHistoryV3(PropertyHistory):
    @cached_property
    def _property_wrapper(self) -> IURLPropertyRepresentation:
        properties = list(self.properties.keys())
        return APIPropertiesWithHistory(properties=properties)

    limit = 50
    more_key = page_filter = page_field = None
    limit_field = "limit"
    data_field = "results"
    additional_keys = ["archived"]
    last_modified_date_field_name = "hs_lastmodifieddate"

    def update_request_properties(self, params: Mapping[str, Any], properties: IURLPropertyRepresentation) -> None:
        pass

    def _transform(self, records: Iterable) -> Iterable:
        for record in records:
            properties_with_history = record.get("propertiesWithHistory")
            primary_key = record.get("id")
            additional_keys = {additional_key: record.get(additional_key) for additional_key in self.additional_keys}

            for property_name, value_dict in properties_with_history.items():
                if property_name == self.last_modified_date_field_name:
                    # Skipping the lastmodifieddate since it only returns the value
                    # when one field of a record was changed no matter which
                    # field was changed. It therefore creates overhead, since for
                    # every changed property there will be the date it was changed in itself
                    # and a change in the lastmodifieddate field.
                    continue
                for version in value_dict:
                    version["property"] = property_name
                    version[self.entity_primary_key] = primary_key
                    yield version | additional_keys


class CompaniesPropertyHistory(PropertyHistoryV3):
    scopes = {"crm.objects.companies.read"}
    properties_scopes = {"crm.schemas.companies.read"}
    entity = "companies"
    entity_primary_key = "companyId"
    primary_key = ["companyId", "property", "timestamp"]

    @property
    def url(self) -> str:
        return "/crm/v3/objects/companies"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> str:
        return f"{self.url}?{properties.as_url_param()}"


class DealsPropertyHistory(PropertyHistoryV3):
    scopes = {"crm.objects.deals.read"}
    properties_scopes = {"crm.schemas.deals.read"}
    entity = "deals"
    entity_primary_key = "dealId"
    primary_key = ["dealId", "property", "timestamp"]

    @property
    def url(self) -> str:
        return "/crm/v3/objects/deals"

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> str:
        return f"{self.url}?{properties.as_url_param()}"


class SubscriptionChanges(IncrementalStream):
    """Subscriptions timeline for a portal, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions_timeline
    """

    url = "/email/public/v1/subscriptions/timeline"
    data_field = "timeline"
    more_key = "hasMore"
    updated_at_field = "timestamp"
    scopes = {"content"}


class Workflows(ClientSideIncrementalStream):
    """Workflows, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows
    """

    url = "/automation/v3/workflows"
    data_field = "workflows"
    updated_at_field = "updatedAt"
    created_at_field = "insertedAt"
    cursor_field_datetime_format = "x"
    primary_key = "id"
    scopes = {"automation"}
    unnest_fields = ["contactListIds"]


class Companies(CRMSearchStream):
    entity = "company"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read", "crm.objects.companies.read"}


class Contacts(CRMSearchStream):
    entity = "contact"
    last_modified_field = "lastmodifieddate"
    associations = ["contacts", "companies"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}
    _transformations = [NewtoLegacyFieldTransformation(field_mapping=CONTACTS_NEW_TO_LEGACY_FIELDS_MAPPING)]


class EngagementsCalls(CRMSearchStream):
    entity = "calls"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deals", "companies", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsEmails(CRMSearchStream):
    entity = "emails"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deals", "companies", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read", "sales-email-read"}


class EngagementsMeetings(CRMSearchStream):
    entity = "meetings"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deals", "companies", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsNotes(CRMSearchStream):
    entity = "notes"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deals", "companies", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsTasks(CRMSearchStream):
    entity = "tasks"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deals", "companies", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


# this stream uses a beta endpoint thus is unstable and disabled
class FeedbackSubmissions(CRMObjectIncrementalStream):
    entity = "feedback_submissions"
    associations = ["contacts"]
    primary_key = "id"
    scopes = {"crm.objects.feedback_submissions.read"}


class Goals(CRMObjectIncrementalStream):
    entity = "goal_targets"
    last_modified_field = "hs_lastmodifieddate"
    primary_key = "id"
    scopes = {"crm.objects.goals.read"}


class Leads(CRMSearchStream):
    entity = "leads"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "companies"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read", "crm.objects.companies.read", "crm.objects.leads.read"}


class LineItems(CRMObjectIncrementalStream):
    entity = "line_item"
    primary_key = "id"
    scopes = {"e-commerce", "crm.objects.line_items.read"}


class Products(CRMObjectIncrementalStream):
    entity = "product"
    primary_key = "id"
    scopes = {"e-commerce"}


class Tickets(CRMSearchStream):
    entity = "ticket"
    associations = ["contacts", "deals", "companies"]
    primary_key = "id"
    scopes = {"tickets"}
    last_modified_field = "hs_lastmodifieddate"


class CustomObject(CRMSearchStream, ABC):
    last_modified_field = "hs_lastmodifieddate"
    primary_key = "id"
    scopes = {"crm.schemas.custom.read", "crm.objects.custom.read"}

    def __init__(self, entity: str, schema: Mapping[str, Any], fully_qualified_name: str, custom_properties: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.schema = schema
        self.fully_qualified_name = fully_qualified_name
        self.custom_properties = custom_properties

    @property
    def name(self) -> str:
        return self.entity

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema

    @property
    def properties(self) -> Mapping[str, Any]:
        # do not make extra api calls
        return self.custom_properties


class EmailSubscriptions(Stream):
    """EMAIL SUBSCRIPTION, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions
    """

    url = "/email/public/v1/subscriptions"
    data_field = "subscriptionDefinitions"
    primary_key = "id"
    scopes = {"content"}
    filter_old_records = False


class WebAnalyticsStream(CheckpointMixin, HttpSubStream, Stream):
    """
    A base class for Web Analytics API
    Docs: https://developers.hubspot.com/docs/api/events/web-analytics
    """

    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    cursor_field: str = "occurredAt"
    slicing_period: int = 30
    state_checkpoint_interval: int = 100

    # Set this flag to `False` as we don't need client side incremental logic
    filter_old_records: bool = False

    def __init__(self, parent: HttpStream, **kwargs: Any):
        super().__init__(parent, **kwargs)
        self._state: MutableMapping[str, Any] = {}

    @property
    def scopes(self) -> Set[str]:
        return getattr(self.parent, "scopes") | {"oauth"}

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def get_json_schema(self):
        raw_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "$ref": "default_event_properties.json",
        }
        return ResourceSchemaLoader("source_hubspot")._resolve_schema_references(raw_schema=raw_schema)

    def get_latest_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        """
        State is a composite object that keeps latest datetime of an event for each parent object:
        {
            "100": {"occurredAt": "2023-11-24T23:23:23.000Z"},
            "200": {"occurredAt": "2023-11-24T23:23:23.000Z"},
            ...,
            "<parent object id>": {"occurredAt": "<datetime string in iso8601 format>"}
        }
        """
        if latest_record["objectId"] in current_stream_state:
            # Not sure whether records are sorted and what kind of sorting is used,
            # so trying to keep higher datetime value
            latest_datetime = max(
                current_stream_state[latest_record["objectId"]][self.cursor_field],
                latest_record[self.cursor_field],
            )
        else:
            latest_datetime = latest_record[self.cursor_field]
        return {**self.state, latest_record["objectId"]: {self.cursor_field: latest_datetime}}

    def records_transformer(self, records: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
        for record in records:
            # We don't need `properties` as all the fields are unnested to the root
            if "properties" in record:
                record.pop("properties")
            yield record

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        now = pendulum.now(tz="UTC")
        for parent_slice in super().stream_slices(sync_mode, cursor_field, stream_state):
            object_id = parent_slice["parent"][self.object_id_field]

            # We require this workaround to shorten the duration of the acceptance test run.
            # The web analytics stream alone takes over 3 hours to complete.
            # Consequently, we aim to run the test against a limited number of object IDs.
            if self._is_test and object_id not in self._acceptance_test_config.get("object_ids", []):
                continue

            # Take the initial datetime either form config or from state depending whichever value is higher
            # In case when state is detected add a 1 millisecond to avoid duplicates from previous sync
            from_datetime = (
                max(
                    self._start_date,
                    self._field_to_datetime(self.state[object_id][self.cursor_field]) + timedelta(milliseconds=1),
                )
                if object_id in self.state
                else self._start_date
            )

            # Making slices of given slice period
            while (
                (to_datetime := min(from_datetime.add(days=self.slicing_period), now)) <= now
                and from_datetime != now
                and from_datetime <= to_datetime
            ):
                yield {
                    "occurredAfter": from_datetime.to_iso8601_string(),
                    "occurredBefore": to_datetime.to_iso8601_string(),
                    "objectId": object_id,
                    "objectType": self.object_type,
                }
                # Shift time window to the next checkpoint interval
                from_datetime = to_datetime

    @property
    def object_type(self) -> str:
        """
        The name of the CRM Object for which Web Analytics is requested
        List of available CRM objects: https://developers.hubspot.com/docs/api/crm/understanding-the-crm
        """
        return getattr(self.parent, "entity")

    @property
    def object_id_field(self) -> str:
        """
        The ID field name of the CRM Object for which Web Analytics is requested
        List of available CRM objects: https://developers.hubspot.com/docs/api/crm/understanding-the-crm
        """
        return getattr(self.parent, "primary_key")

    @property
    def url(self) -> str:
        return "/events/v3/events"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Preparing the request params dictionary for the following query string:
        <url>?objectType=<parent-type>
             &objectId=<parent-id>
             &occurredAfter=<event-datetime-iso8601>
             &occurredBefore=<event-datetime-iso8601>
        """
        params = super().request_params(stream_state, stream_slice, next_page_token)
        return params | stream_slice

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        record_generator = super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

        record_generator = self.records_transformer(record_generator)
        for record in record_generator:
            yield record
            # Update state with latest datetime each time we have a record
            if sync_mode == SyncMode.incremental:
                self.state = self.get_latest_state(self.state, record)


class ContactsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Contacts(**kwargs), **kwargs)


class CompaniesWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Companies(**kwargs), **kwargs)


class DealsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Deals(**kwargs), **kwargs)


class TicketsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Tickets(**kwargs), **kwargs)


class EngagementsCallsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=EngagementsCalls(**kwargs), **kwargs)


class EngagementsEmailsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=EngagementsEmails(**kwargs), **kwargs)


class EngagementsMeetingsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=EngagementsMeetings(**kwargs), **kwargs)


class EngagementsNotesWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=EngagementsNotes(**kwargs), **kwargs)


class EngagementsTasksWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=EngagementsTasks(**kwargs), **kwargs)


class GoalsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Goals(**kwargs), **kwargs)


class LineItemsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=LineItems(**kwargs), **kwargs)


class ProductsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=Products(**kwargs), **kwargs)


class FeedbackSubmissionsWebAnalytics(WebAnalyticsStream):
    def __init__(self, **kwargs: Any):
        super().__init__(parent=FeedbackSubmissions(**kwargs), **kwargs)
