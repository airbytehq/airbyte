#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
import time
import urllib.parse
from abc import ABC, abstractmethod
from functools import lru_cache, partial
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import backoff
import pendulum as pendulum
import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from source_hubspot.errors import HubspotAccessDenied, HubspotInvalidAuth, HubspotRateLimited, HubspotTimeout

# The value is obtained experimentally, HubSpot allows the URL length up to ~16300 symbols,
# so it was decided to limit the length of the `properties` parameter to 15000 characters.
PROPERTIES_PARAM_MAX_LENGTH = 15000

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


def split_properties(properties_list: List[str]) -> Iterator[Tuple[str]]:
    summary_length = 0
    local_properties = []
    for property_ in properties_list:
        if len(property_) + summary_length + len(urllib.parse.quote(",")) >= PROPERTIES_PARAM_MAX_LENGTH:
            yield local_properties
            local_properties = []
            summary_length = 0

        local_properties.append(property_)
        summary_length += len(property_) + len(urllib.parse.quote(","))

    if local_properties:
        yield local_properties


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

    def __init__(self, credentials: Mapping[str, Any]):
        self._session = requests.Session()
        credentials_title = credentials.get("credentials_title")

        if credentials_title == "OAuth Credentials":
            self._session.auth = Oauth2Authenticator(
                token_refresh_endpoint=self.BASE_URL + "/oauth/v1/token",
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
                refresh_token=credentials["refresh_token"],
            )
        elif credentials_title == "API Key Credentials":
            self._session.params["hapikey"] = credentials.get("api_key")
        else:
            raise Exception("No supported `credentials_title` specified. See spec.json for references")

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
    def get(self, url: str, params: MutableMapping[str, Any] = None) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        response = self._session.get(self.BASE_URL + url, params=params)
        return self._parse_and_handle_errors(response)

    def post(
        self, url: str, data: Mapping[str, Any], params: MutableMapping[str, Any] = None
    ) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        response = self._session.post(self.BASE_URL + url, params=params, json=data)
        return self._parse_and_handle_errors(response)


class Stream(ABC):
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

    @property
    @abstractmethod
    def url(self):
        """Default URL to read from"""

    def __init__(self, api: API, start_date: str = None, **kwargs):
        self._api: API = api
        self._start_date = pendulum.parse(start_date)

    @property
    def name(self) -> str:
        stream_name = self.__class__.__name__
        if stream_name.endswith("Stream"):
            stream_name = stream_name[: -len("Stream")]
        return stream_name

    def list_records(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))

    @staticmethod
    def _cast_value(declared_field_types: List, field_name: str, field_value: Any, declared_format: str = None) -> Any:
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

        actual_field_type = type(field_value)
        actual_field_type_name = CUSTOM_FIELD_TYPE_TO_VALUE.get(actual_field_type)
        if actual_field_type_name in declared_field_types:
            return field_value

        target_type_name = next(filter(lambda t: t != "null", declared_field_types))
        target_type = CUSTOM_FIELD_VALUE_TO_TYPE.get(target_type_name)

        if target_type_name == "number":
            # do not cast numeric IDs into float, use integer instead
            target_type = int if field_name.endswith("_id") else target_type

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

    def _read_stream_records(
        self, getter: Callable, properties_list: List[str], params: MutableMapping[str, Any] = None
    ) -> Tuple[dict, Any]:
        # TODO: Additional processing was added due to the fact that users receive 414 errors while syncing their streams (issues #3977 and #5835).
        #  We will need to fix this code when the HubSpot developers add the ability to use a special parameter to get all properties for an entity.
        #  According to HubSpot Community (https://community.hubspot.com/t5/APIs-Integrations/Get-all-contact-properties-without-explicitly-listing-them/m-p/447950)
        #  and the official documentation, this does not exist at the moment.
        stream_records = {}
        response = None

        for properties in split_properties(properties_list):
            params.update({"properties": ",".join(properties)})
            response = getter(params=params)
            for record in self._transform(self.parse_response(response)):
                if record["id"] not in stream_records:
                    stream_records[record["id"]] = record
                elif stream_records[record["id"]].get("properties"):
                    stream_records[record["id"]]["properties"].update(record.get("properties", {}))

        return stream_records, response

    def _read(self, getter: Callable, params: MutableMapping[str, Any] = None) -> Iterator:
        next_page_token = None
        while True:
            if next_page_token:
                params.update(next_page_token)

            properties_list = list(self.properties.keys())
            if properties_list:
                stream_records, response = self._read_stream_records(getter=getter, params=params, properties_list=properties_list)
                yield from [value for key, value in stream_records.items()]
            else:
                response = getter(params=params)
                yield from self._transform(self.parse_response(response))

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                break

    def read(self, getter: Callable, params: Mapping[str, Any] = None, filter_old_records: bool = True) -> Iterator:
        default_params = {self.limit_field: self.limit}
        params = {**default_params, **params} if params else {**default_params}
        generator = self._read(getter, params)
        if filter_old_records:
            generator = self._filter_old_records(generator)

        yield from generator

    def parse_response(self, response: Union[Mapping[str, Any], List[dict]]) -> Iterator:
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
                logger.warning(f"Stream `{self.name}` cannot be procced. {response.get('message')}")
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

    def next_page_token(self, response: Union[Mapping[str, Any], List[dict]]) -> Optional[Mapping[str, Union[int, str]]]:
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
        data = self._api.get(f"/properties/v2/{self.entity}/properties")
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

    @property
    @abstractmethod
    def updated_at_field(self):
        """Name of the field associated with the state"""

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return (
                {self.state_pk: int(self._state.timestamp() * 1000)} if self.state_pk == "timestamp" else {self.state_pk: str(self._state)}
            )
        return None

    @state.setter
    def state(self, value):
        state = value[self.state_pk]
        self._state = pendulum.parse(str(pendulum.from_timestamp(state / 1000))) if isinstance(state, int) else pendulum.parse(state)
        self._start_date = max(self._state, self._start_date)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Apply state filter to set of records, update cursor(state) if necessary in the end"""
        latest_cursor = None
        # to track state, there is no guarantee that returned records sorted in ascending order. Having exact
        # boundary we could always ensure we don't miss records between states. In the future, if we would
        # like to save the state more often we can do this every batch
        for record in self.read_chunked(getter, params):
            yield record
            cursor = self._field_to_datetime(record[self.updated_at_field])
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor

        self._update_state(latest_cursor=latest_cursor)

    def _update_state(self, latest_cursor):
        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state

    def read_chunked(
        self, getter: Callable, params: Mapping[str, Any] = None, chunk_size: pendulum.duration = pendulum.duration(days=30)
    ) -> Iterator:
        params = {**params} if params else {}
        now_ts = int(pendulum.now().timestamp() * 1000)
        start_ts = int(self._start_date.timestamp() * 1000)
        max_delta = now_ts - start_ts
        chunk_size = int(chunk_size.total_seconds() * 1000) if self.need_chunk else max_delta

        for ts in range(start_ts, now_ts, chunk_size):
            end_ts = ts + chunk_size
            params["startTimestamp"] = ts
            params["endTimestamp"] = end_ts
            logger.info(
                f"Reading chunk from stream {self.name} between {pendulum.from_timestamp(ts / 1000)} and {pendulum.from_timestamp(end_ts / 1000)}"
            )
            yield from super().read(getter, params)


class CRMSearchStream(IncrementalStream, ABC):

    limit = 100  # This value is used only when state is None.
    state_pk = "updatedAt"
    updated_at_field = "updatedAt"

    @property
    def url(self):
        return f"/crm/v3/objects/{self.entity}/search" if self.state else f"/crm/v3/objects/{self.entity}"

    def __init__(
        self,
        entity: Optional[str] = None,
        last_modified_field: Optional[str] = None,
        associations: Optional[List[str]] = None,
        include_archived_only: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._state = None
        self.entity = entity
        self.last_modified_field = last_modified_field
        self.associations = associations
        self._include_archived_only = include_archived_only

    @retry_connection_handler(max_tries=5, factor=5)
    @retry_after_handler(fixed_retry_after=1, max_tries=3)
    def search(
        self, url: str, data: Mapping[str, Any], params: MutableMapping[str, Any] = None
    ) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        # We can safely retry this POST call, because it's a search operation.
        # Given Hubspot does not return any Retry-After header (https://developers.hubspot.com/docs/api/crm/search)
        # from the search endpoint, it waits one second after trying again.
        # As per their docs: `These search endpoints are rate limited to four requests per second per authentication token`.
        return self._api.post(url=url, data=data, params=params)

    def list_records(self, fields) -> Iterable:
        params = {
            "archived": str(self._include_archived_only).lower(),
            "associations": self.associations,
        }
        if self.state:
            generator = self.read(partial(self.search, url=self.url), params)
        else:
            generator = self.read(partial(self._api.get, url=self.url), params)
        yield from self._flat_associations(self._filter_old_records(generator))

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Apply state filter to set of records, update cursor(state) if necessary in the end"""
        latest_cursor = None
        default_params = {"limit": self.limit}
        params = {**default_params, **params} if params else {**default_params}
        properties_list = list(self.properties.keys())

        payload = (
            {
                "filters": [{"value": int(self._state.timestamp() * 1000), "propertyName": self.last_modified_field, "operator": "GTE"}],
                "properties": properties_list,
                "limit": 100,
            }
            if self.state
            else {}
        )

        while True:
            stream_records = {}
            if self.state:
                response = getter(data=payload)
                for record in self._transform(self.parse_response(response)):
                    stream_records[record["id"]] = record
            else:
                stream_records, response = self._read_stream_records(getter=getter, params=params, properties_list=properties_list)

            for _, record in stream_records.items():
                yield record
                cursor = self._field_to_datetime(record[self.updated_at_field])
                latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            if "paging" in response and "next" in response["paging"] and "after" in response["paging"]["next"]:
                params["after"] = response["paging"]["next"]["after"]
                payload["after"] = response["paging"]["next"]["after"]
            else:
                break

        self._update_state(latest_cursor=latest_cursor)


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

    def __init__(
        self, entity: Optional[str] = None, associations: Optional[List[str]] = None, include_archived_only: bool = False, **kwargs
    ):
        super().__init__(**kwargs)
        self.entity = entity or self.entity
        self.associations = associations or self.associations
        self._include_archived_only = include_archived_only

        if not self.entity:
            raise ValueError("Entity must be set either on class or instance level")

    def list_records(self, fields) -> Iterable:
        params = {
            "archived": str(self._include_archived_only).lower(),
            "associations": self.associations,
        }
        generator = self.read(partial(self._api.get, url=self.url), params)
        yield from self._flat_associations(generator)


class CRMObjectIncrementalStream(CRMObjectStream, IncrementalStream):
    state_pk = "updatedAt"
    limit = 100
    need_chunk = False


class CampaignStream(Stream):
    """Email campaigns, API v1
    There is some confusion between emails and campaigns in docs, this endpoint returns actual emails
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_campaign_data
    """

    url = "/email/public/v1/campaigns"
    more_key = "hasMore"
    data_field = "campaigns"
    limit = 500
    updated_at_field = "lastUpdatedTime"

    def list_records(self, fields) -> Iterable:
        for row in self.read(getter=partial(self._api.get, url=self.url)):
            record = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            yield {**row, **record}


class ContactListStream(IncrementalStream):
    """Contact lists, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/lists/get_lists
    """

    url = "/contacts/v1/lists"
    data_field = "lists"
    more_key = "has-more"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    limit_field = "count"
    need_chunk = False


class ContactsListMembershipsStream(Stream):
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

    def list_records(self, fields) -> Iterable:
        """Receiving all contacts with list memberships"""
        params = {"showListMemberships": True}
        yield from self.read(partial(self._api.get, url=self.url), params)


class DealStageHistoryStream(Stream):
    """Deal stage history, API v1
    Deal stage history is exposed by the v1 API, but not the v3 API.
    The v1 endpoint requires the contacts scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/deals/get-all-deals
    """

    url = "/deals/v1/deal/paged"
    more_key = "hasMore"
    data_field = "deals"
    updated_at_field = "timestamp"

    def _transform(self, records: Iterable) -> Iterable:
        for record in super()._transform(records):
            dealstage = record.get("properties", {}).get("dealstage", {})
            updated_at = dealstage.get(self.updated_at_field)
            if updated_at:
                yield {"id": record.get("dealId"), "dealstage": dealstage, self.updated_at_field: updated_at}

    def list_records(self, fields) -> Iterable:
        params = {"propertiesWithHistory": "dealstage"}
        yield from self.read(partial(self._api.get, url=self.url), params)


class DealStream(CRMSearchStream):
    """Deals, API v3"""

    def __init__(self, **kwargs):
        super().__init__(entity="deal", last_modified_field="hs_lastmodifieddate", **kwargs)
        self._stage_history = DealStageHistoryStream(**kwargs)

    def list_records(self, fields) -> Iterable:
        history_by_id = {}
        for record in self._stage_history.list_records(fields):
            if all(field in record for field in ("id", "dealstage")):
                history_by_id[record["id"]] = record["dealstage"]
        for record in super().list_records(fields):
            if record.get("id") and int(record["id"]) in history_by_id:
                record["dealstage"] = history_by_id[int(record["id"])]
            yield record


class DealPipelineStream(Stream):
    """Deal pipelines, API v1,
    This endpoint requires the contacts scope the tickets scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """

    url = "/crm-pipelines/v1/pipelines/deals"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


class TicketPipelineStream(Stream):
    """Ticket pipelines, API v1
    This endpoint requires the tickets scope.
    Docs: https://developers.hubspot.com/docs/api/crm/pipelines
    """

    url = "/crm/v3/pipelines/tickets"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


class EmailEventStream(IncrementalStream):
    """Email events, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_events
    """

    url = "/email/public/v1/events"
    data_field = "events"
    more_key = "hasMore"
    updated_at_field = "created"
    created_at_field = "created"


class EngagementStream(IncrementalStream):
    """Engagements, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements
          https://legacydocs.hubspot.com/docs/methods/engagements/get-recent-engagements
    """

    url = "/engagements/v1/engagements/paged"
    more_key = "hasMore"
    limit = 250
    updated_at_field = "lastUpdated"
    created_at_field = "createdAt"
    state_pk = "lastUpdated"

    @property
    def url(self):
        if self.state:
            return "/engagements/v1/engagements/recent/modified"
        return "/engagements/v1/engagements/paged"

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        return {self.state_pk: self._state} if self._state else None

    @state.setter
    def state(self, value):
        state = value[self.state_pk]
        self._state = state
        self._start_date = max(self._field_to_datetime(self._state), self._start_date)

    def _transform(self, records: Iterable) -> Iterable:
        yield from super()._transform({**record.pop("engagement"), **record} for record in records)

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        max_last_updated_at = None
        default_params = {self.limit_field: self.limit}
        params = {**default_params, **params} if params else {**default_params}
        if self.state:
            params["since"] = self._state
        count = 0
        for record in self._filter_old_records(self._read(getter, params)):
            yield record
            count += 1
            cursor = record[self.updated_at_field]
            max_last_updated_at = max(cursor, max_last_updated_at) if max_last_updated_at else cursor

        logger.info(f"Processed {count} records")

        if max_last_updated_at:
            new_state = max(max_last_updated_at, self._state) if self._state else max_last_updated_at
            if new_state != self._state:
                logger.info(f"Advancing bookmark for engagement stream from {self._state} to {max_last_updated_at}")
                self._state = new_state
                self._start_date = self._state


class FormStream(Stream):
    """Marketing Forms, API v3
    by default non-marketing forms are filtered out of this endpoint
    Docs: https://developers.hubspot.com/docs/api/marketing/forms
    """

    entity = "form"
    url = "/marketing/v3/forms"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


class FormSubmissionStream(Stream):
    """Marketing Forms, API v1
    This endpoint requires the forms scope.
    Docs: https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form
    """

    url = "/form-integrations/v1/submissions/forms"
    limit = 50
    updated_at_field = "updatedAt"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forms = FormStream(**kwargs)

    def _transform(self, records: Iterable) -> Iterable:
        for record in super()._transform(records):
            keys = record.keys()

            # There's no updatedAt field in the submission however forms fetched by using this field,
            # so it has to be added to the submissions otherwise it would fail when calling _filter_old_records
            if "updatedAt" not in keys:
                record["updatedAt"] = record["submittedAt"]

            yield record

    def list_records(self, fields) -> Iterable:
        seen = set()
        # To get submissions for all forms date filtering has to be disabled
        for form in self.forms.read(getter=partial(self.forms._api.get, url=self.forms.url), filter_old_records=False):
            if form["id"] not in seen:
                seen.add(form["id"])
                for submission in self.read(getter=partial(self._api.get, url=f"{self.url}/{form['id']}")):
                    submission["formId"] = form["id"]
                    yield submission


class MarketingEmailStream(Stream):
    """Marketing Email, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-emails
    """

    url = "/marketing-emails/v1/emails/with-statistics"
    data_field = "objects"
    limit = 250
    updated_at_field = "updated"
    created_at_field = "created"


class OwnerStream(Stream):
    """Owners, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/owners/get_owners
    """

    url = "/crm/v3/owners"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


class PropertyHistoryStream(IncrementalStream):
    """Contacts Endpoint, API v1
    Is used to get all Contacts and the history of their respective
    Properties. Whenever a property is changed it is added here.
    Docs: https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts
    """

    more_key = "has-more"
    url = "/contacts/v1/lists/recently_updated/contacts/recent"
    updated_at_field = "timestamp"
    created_at_field = "timestamp"
    data_field = "contacts"
    page_field = "vid-offset"
    page_filter = "vidOffset"
    limit = 100

    def list(self, fields) -> Iterable:
        properties = self._api.get("/properties/v2/contact/properties")
        properties_list = [single_property["name"] for single_property in properties]
        params = {"propertyMode": "value_and_history", "property": properties_list}
        yield from self.read(partial(self._api.get, url=self.url), params)

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
                        version["timestamp"] = self._field_to_datetime(version["timestamp"]).to_datetime_string()
                        version["property"] = key
                        version["vid"] = vid
                        yield version


class SubscriptionChangeStream(IncrementalStream):
    """Subscriptions timeline for a portal, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/email/get_subscriptions_timeline
    """

    url = "/email/public/v1/subscriptions/timeline"
    data_field = "timeline"
    more_key = "hasMore"
    updated_at_field = "timestamp"


class WorkflowStream(Stream):
    """Workflows, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows
    """

    url = "/automation/v3/workflows"
    data_field = "workflows"
    updated_at_field = "updatedAt"
    created_at_field = "insertedAt"
