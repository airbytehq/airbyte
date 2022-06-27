#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import sys
import time
from abc import ABC, abstractmethod
from functools import cached_property, lru_cache
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union

import backoff
import pendulum as pendulum
import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests import codes
from source_hubspot.errors import HubspotAccessDenied, HubspotInvalidAuth, HubspotRateLimited, HubspotTimeout
from source_hubspot.helpers import APIv1Property, APIv3Property, GroupByKey, IRecordPostProcessor, IURLPropertyRepresentation, StoreAsIs

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


def retry_connection_handler(**kwargs):
    """Retry helper, log each attempt"""

    def log_retry_attempt(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def giveup_handler(exc):
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


class API:
    """HubSpot API interface, authorize, retrieve and post, supports backoff logic"""

    BASE_URL = "https://api.hubapi.com"
    USER_AGENT = "Airbyte"

    def is_oauth2(self) -> bool:
        credentials_title = self.credentials.get("credentials_title")

        return credentials_title == "OAuth Credentials"

    def get_authenticator(self) -> Optional[Oauth2Authenticator]:
        if self.is_oauth2():
            return Oauth2Authenticator(
                token_refresh_endpoint=self.BASE_URL + "/oauth/v1/token",
                client_id=self.credentials["client_id"],
                client_secret=self.credentials["client_secret"],
                refresh_token=self.credentials["refresh_token"],
            )
        else:
            return None

    def __init__(self, credentials: Mapping[str, Any]):
        self._session = requests.Session()
        self.credentials = credentials
        credentials_title = credentials.get("credentials_title")

        if self.is_oauth2():
            self._session.auth = self.get_authenticator()
        elif credentials_title == "API Key Credentials":
            self._session.params["hapikey"] = credentials.get("api_key")
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

        if response.status_code == HTTPStatus.FORBIDDEN:
            """Once hit the forbidden endpoint, we return the error message from response."""
            pass
        elif response.status_code in (HTTPStatus.UNAUTHORIZED, CLOUDFLARE_ORIGIN_DNS_ERROR):
            raise HubspotInvalidAuth(message, response=response)
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            raise HubspotRateLimited(
                f"429 Rate Limit Exceeded: API rate-limit has been reached until {retry_after} seconds."
                " See https://developers.hubspot.com/docs/api/usage-details",
                response=response,
            )
        elif response.status_code in (HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE):
            raise HubspotTimeout(message, response=response)
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


class Stream(HttpStream, ABC):
    """Base class for all streams. Responsible for data fetching and pagination"""

    entity: str = None
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

    @property
    @abstractmethod
    def scopes(self) -> Set[str]:
        """Set of required scopes. Users need to grant at least one of the scopes for the stream to be avaialble to them"""

    def scope_is_granted(self, granted_scopes: Set[str]) -> bool:
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
    ) -> str:
        return self.url

    @cached_property
    def _property_wrapper(self) -> IURLPropertyRepresentation:
        properties = list(self.properties.keys())
        if "v1" in self.url:
            return APIv1Property(properties)
        return APIv3Property(properties)

    def __init__(self, api: API, start_date: str = None, credentials: Mapping[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self._api: API = api
        self._start_date = pendulum.parse(start_date)

        if credentials["credentials_title"] == "API Key Credentials":
            self._session.params["hapikey"] = credentials.get("api_key")

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
            json_schema["properties"]["properties"] = {"type": "object", "properties": self.properties}
        return json_schema

    def handle_request(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        properties: IURLPropertyRepresentation = None,
    ) -> requests.Response:
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if properties:
            request_params.update(properties.as_url_param())

        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
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
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
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
                yield from records

                next_page_token = self.next_page_token(response)
                if not next_page_token:
                    pagination_complete = True

            # Always return an empty generator just in case no records were ever yielded
            yield from []
        except requests.exceptions.HTTPError as e:
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

        if target_type_name == "number":
            # do not cast numeric IDs into float, use integer instead
            target_type = int if field_name.endswith("_id") else target_type
            field_value = field_value.replace(",", "")

        if target_type_name != "string" and field_value == "":
            # do not cast empty strings, return None instead to be properly casted.
            field_value = None
            return field_value

        try:
            casted_value = target_type(field_value)
        except ValueError:
            logger.exception(f"Could not cast `{field_value}` to `{target_type}`")
            return field_value

        return casted_value

    def _cast_record_fields_if_needed(self, record: Mapping, properties: Mapping[str, Any] = None) -> Mapping:

        if not self.entity or not record.get("properties"):
            return record

        properties = properties or self.properties

        for field_name, field_value in record["properties"].items():
            declared_field_types = properties[field_name].get("type", [])
            if not isinstance(declared_field_types, Iterable):
                declared_field_types = [declared_field_types]
            format = properties[field_name].get("format")
            record["properties"][field_name] = self._cast_value(
                declared_field_types=declared_field_types, field_name=field_name, field_value=field_value, declared_format=format
            )

        return record

    def _transform(self, records: Iterable) -> Iterable:
        """Preprocess record before emitting"""
        for record in records:
            record = self._cast_record_fields_if_needed(record)
            if self.created_at_field and self.updated_at_field and record.get(self.updated_at_field) is None:
                record[self.updated_at_field] = record[self.created_at_field]
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
                if not response.get(self.more_key, False):
                    return
                if self.page_field in response:
                    return {self.page_filter: response[self.page_field]}
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
            logger.warn(f"Unsupported type {field_type} found")

        field_props = {
            "type": ["null", converted_type or field_type],
        }

        if field_format:
            field_props["format"] = field_format

        return field_props

    @property
    @lru_cache()
    def properties(self) -> Mapping[str, Any]:
        """Some entities has dynamic set of properties, so we trying to resolve those at runtime"""
        if not self.entity:
            return {}

        props = {}
        data, response = self._api.get(f"/properties/v2/{self.entity}/properties")
        for row in data:
            props[row["name"]] = self._get_field_props(row["type"])

        return props

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
                    record[name] = [row["id"] for row in association.get("results", [])]
            yield record


class IncrementalStream(Stream, ABC):
    """Stream that supports state and incremental read"""

    state_pk = "timestamp"
    limit = 1000
    # Flag which enable/disable chunked read in read_chunked method
    # False -> chunk size is max (only one slice), True -> chunk_size is 30 days
    need_chunk = True
    state_checkpoint_interval = 500

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
        self._update_state(latest_cursor=latest_cursor)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return self.state

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

    def _update_state(self, latest_cursor):
        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state

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
    associations: List[str] = None

    @property
    def url(self):
        return f"/crm/v3/objects/{self.entity}/search" if self.state else f"/crm/v3/objects/{self.entity}"

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
    ) -> Tuple[List, requests.Response]:
        stream_records = {}
        properties_list = list(self.properties.keys())
        payload = (
            {
                "filters": [{"value": int(self._state.timestamp() * 1000), "propertyName": self.last_modified_field, "operator": "GTE"}],
                "sorts": [{"propertyName": self.last_modified_field, "direction": "ASCENDING"}],
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

        latest_cursor = None
        while not pagination_complete:
            if self.state:
                records, raw_response = self._process_search(
                    next_page_token=next_page_token,
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                )

            else:
                records, raw_response = self._read_stream_records(
                    stream_slice=stream_slice,
                    stream_state=stream_state,
                    next_page_token=next_page_token,
                )
            records = self._filter_old_records(records)
            records = self._flat_associations(records)

            for record in records:
                cursor = self._field_to_datetime(record[self.updated_at_field])
                latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
                yield record

            next_page_token = self.next_page_token(raw_response)
            if not next_page_token:
                pagination_complete = True
            elif self.state and next_page_token["payload"]["after"] >= 10000:
                # Hubspot documentation states that the search endpoints are limited to 10,000 total results
                # for any given query. Attempting to page beyond 10,000 will result in a 400 error.
                # https://developers.hubspot.com/docs/api/crm/search. We stop getting data at 10,000 and
                # start a new search query with the latest state that has been collected.
                self._update_state(latest_cursor=latest_cursor)
                next_page_token = None

        self._update_state(latest_cursor=latest_cursor)
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
        self.set_sync(sync_mode)
        return [None]


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


class Campaigns(Stream):
    """Email campaigns, API v1
    There is some confusion between emails and campaigns in docs, this endpoint returns actual emails
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_campaign_data
    """

    url = "/email/public/v1/campaigns"
    more_key = "hasMore"
    data_field = "campaigns"
    limit = 500
    updated_at_field = "lastUpdatedTime"
    primary_key = "id"
    scopes = {"crm.lists.read"}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for row in super().read_records(sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state):
            record, response = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            yield {**row, **record}


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
    need_chunk = False
    scopes = {"crm.lists.read"}


class ContactsListMemberships(Stream):
    """Contacts list Memberships, API v1
    The Stream was created due to issue #8477, where supporting List Memberships in Contacts stream was requested.
    According to the issue this feature is supported in API v1 by setting parameter showListMemberships=true
    in get all contacts endpoint. API will return list memberships for each contact record.
    But for syncing Contacts API v3 is used, where list memberships for contacts isn't supported.
    Therefore, new stream was created based on get all contacts endpoint of API V1.
    Docs: https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts
    """

    url = "/contacts/v1/lists/all/contacts/all"
    updated_at_field = "timestamp"
    more_key = "has-more"
    data_field = "contacts"
    page_filter = "vidOffset"
    page_field = "vid-offset"
    primary_key = "canonical-vid"
    scopes = {"crm.objects.contacts.read"}

    def _transform(self, records: Iterable) -> Iterable:
        """Extracting list membership records from contacts
        According to documentation Contacts may have multiple vids,
        but the canonical-vid will be the primary ID for a record.
        Docs: https://legacydocs.hubspot.com/docs/methods/contacts/contacts-overview
        """
        for record in super()._transform(records):
            canonical_vid = record.get("canonical-vid")
            for item in record.get("list-memberships", []):
                yield {"canonical-vid": canonical_vid, **item}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"showListMemberships": True})
        return params


class Deals(CRMSearchStream):
    """Deals, API v3"""

    entity = "deal"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "companies", "line_items"]
    primary_key = "id"
    scopes = {"contacts", "crm.objects.deals.read"}


class DealPipelines(Stream):
    """Deal pipelines, API v1,
    This endpoint requires the contacts scope the tickets scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """

    url = "/crm-pipelines/v1/pipelines/deals"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    primary_key = "pipelineId"
    scopes = {"contacts", "tickets"}


class TicketPipelines(Stream):
    """Ticket pipelines, API v1
    This endpoint requires the tickets scope.
    Docs: https://developers.hubspot.com/docs/api/crm/pipelines
    """

    url = "/crm/v3/pipelines/tickets"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
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


class Engagements(IncrementalStream):
    """Engagements, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements
          https://legacydocs.hubspot.com/docs/methods/engagements/get-recent-engagements
    """

    url = "/engagements/v1/engagements/paged"
    more_key = "hasMore"
    updated_at_field = "lastUpdated"
    created_at_field = "createdAt"
    primary_key = "id"
    scopes = {"crm.objects.companies.read", "crm.objects.contacts.read", "crm.objects.deals.read", "tickets", "e-commerce"}

    @property
    def url(self):
        if self.state:
            return "/engagements/v1/engagements/recent/modified"
        return "/engagements/v1/engagements/paged"

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
        if self.state:
            params.update({"since": int(self._state.timestamp() * 1000), "count": 100})
        return params

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.set_sync(sync_mode)
        return [None]

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
        latest_cursor = None

        while not pagination_complete:
            response = self.handle_request(stream_slice=stream_slice, stream_state=stream_state, next_page_token=next_page_token)
            records = self._transform(self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice))

            if self.filter_old_records:
                records = self._filter_old_records(records)

            for record in records:
                cursor = self._field_to_datetime(record[self.updated_at_field])
                latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
                yield record

            next_page_token = self.next_page_token(response)
            if self.state and next_page_token and next_page_token["offset"] >= 10000:
                # As per Hubspot documentation, the recent engagements endpoint will only return the 10K
                # most recently updated engagements. Since they are returned sorted by `lastUpdated` in
                # descending order, we stop getting records if we have already reached 10,000. Attempting
                # to get more than 10K will result in a HTTP 400 error.
                # https://legacydocs.hubspot.com/docs/methods/engagements/get-recent-engagements
                next_page_token = None

            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []

        self._update_state(latest_cursor=latest_cursor)


class Forms(Stream):
    """Marketing Forms, API v3
    by default non-marketing forms are filtered out of this endpoint
    Docs: https://developers.hubspot.com/docs/api/marketing/forms
    """

    entity = "form"
    url = "/marketing/v3/forms"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    primary_key = "id"
    scopes = {"forms"}


class FormSubmissions(Stream):
    """Marketing Forms, API v1
    This endpoint requires the forms scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form
    """

    url = "/form-integrations/v1/submissions/forms"
    limit = 50
    updated_at_field = "updatedAt"
    scopes = {"forms"}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
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
            record["formId"] = stream_slice["form_id"]
            yield record


class MarketingEmails(Stream):
    """Marketing Email, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-emails
    """

    url = "/marketing-emails/v1/emails/with-statistics"
    data_field = "objects"
    limit = 250
    updated_at_field = "updated"
    created_at_field = "created"
    primary_key = "id"
    scopes = {"content"}


class Owners(Stream):
    """Owners, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/owners/get_owners
    """

    url = "/crm/v3/owners"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    primary_key = "id"
    scopes = {"crm.objects.owners.read"}


class PropertyHistory(IncrementalStream):
    """Contacts Endpoint, API v1
    Is used to get all Contacts and the history of their respective
    Properties. Whenever a property is changed it is added here.
    Docs: https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts
    """

    more_key = "has-more"
    url = "/contacts/v1/lists/recently_updated/contacts/recent"
    updated_at_field = "timestamp"
    created_at_field = "timestamp"
    entity = "contacts"
    data_field = "contacts"
    page_field = "vid-offset"
    page_filter = "vidOffset"
    denormalize_records = True
    limit = 100
    scopes = {"crm.objects.contacts.read"}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(propertyMode="value_and_history")
        return params

    def _transform(self, records: Iterable) -> Iterable:
        for record in records:
            properties = record.get("properties")
            vid = record.get("vid")
            value_dict: Dict
            for key, value_dict in properties.items():
                versions = value_dict.get("versions")
                if key == "lastmodifieddate":
                    # Skipping the lastmodifieddate since it only returns the value
                    # when one field of a contact was changed no matter which
                    # field was changed. It therefore creates overhead, since for
                    # every changed property there will be the date it was changed in itself
                    # and a change in the lastmodifieddate field.
                    continue
                if versions:
                    for version in versions:
                        version["property"] = key
                        version["vid"] = vid
                        yield version


class SubscriptionChanges(IncrementalStream):
    """Subscriptions timeline for a portal, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions_timeline
    """

    url = "/email/public/v1/subscriptions/timeline"
    data_field = "timeline"
    more_key = "hasMore"
    updated_at_field = "timestamp"
    scopes = {"content"}


class Workflows(Stream):
    """Workflows, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows
    """

    url = "/automation/v3/workflows"
    data_field = "workflows"
    updated_at_field = "updatedAt"
    created_at_field = "insertedAt"
    primary_key = "id"
    scopes = {"automation"}


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


class EngagementsCalls(CRMSearchStream):
    entity = "calls"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deal", "company", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsEmails(CRMSearchStream):
    entity = "emails"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deal", "company", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read", "sales-email-read"}


class EngagementsMeetings(CRMSearchStream):
    entity = "meetings"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deal", "company", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsNotes(CRMSearchStream):
    entity = "notes"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deal", "company", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class EngagementsTasks(CRMSearchStream):
    entity = "tasks"
    last_modified_field = "hs_lastmodifieddate"
    associations = ["contacts", "deal", "company", "tickets"]
    primary_key = "id"
    scopes = {"crm.objects.contacts.read"}


class FeedbackSubmissions(CRMObjectIncrementalStream):
    entity = "feedback_submissions"
    associations = ["contacts"]
    primary_key = "id"
    scopes = {"crm.objects.feedback_submissions.read"}


class LineItems(CRMObjectIncrementalStream):
    entity = "line_item"
    primary_key = "id"
    scopes = {"e-commerce"}


class Products(CRMObjectIncrementalStream):
    entity = "product"
    primary_key = "id"
    scopes = {"e-commerce"}


class Tickets(CRMObjectIncrementalStream):
    entity = "ticket"
    associations = ["contacts", "deals", "companies"]
    primary_key = "id"
    scopes = {"tickets"}


class Quotes(CRMObjectIncrementalStream):
    entity = "quote"
    associations = ["deals"]
    primary_key = "id"
    scopes = {"e-commerce"}
