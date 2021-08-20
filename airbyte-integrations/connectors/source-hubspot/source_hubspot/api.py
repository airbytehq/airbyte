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
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import lru_cache, partial
from http import HTTPStatus
from typing import Any, Callable, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

import backoff
import pendulum as pendulum
import requests
from base_python.entrypoint import logger
from source_hubspot.errors import HubspotAccessDenied, HubspotInvalidAuth, HubspotRateLimited, HubspotTimeout

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
    "date": ("string", "date-time"),
    "date-time": ("string", "date-time"),
    "datetime": ("string", "date-time"),
    "json": ("string", None),
    "phone_number": ("string", None),
}

CUSTOM_FIELD_VALUE_TYPE_CAST = {
    bool: "boolean",
    str: "string",
    float: "number",
    int: "integer",
}

CUSTOM_FIELD_VALUE_TYPE_CAST_REVERSED = {v: k for k, v in CUSTOM_FIELD_VALUE_TYPE_CAST.items()}


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


def retry_after_handler(**kwargs):
    """Retry helper when we hit the call limit, sleeps for specific duration"""

    def sleep_on_ratelimit(_details):
        _, exc, _ = sys.exc_info()
        if isinstance(exc, HubspotRateLimited):
            # Hubspot API does not always return Retry-After value for 429 HTTP error
            retry_after = int(exc.response.headers.get("Retry-After", 3))
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
    """Hubspot API interface, authorize, retrieve and post, supports backoff logic"""

    BASE_URL = "https://api.hubapi.com"
    USER_AGENT = "Airbyte"

    def __init__(self, credentials: Mapping[str, Any]):
        self._credentials = {**credentials}
        self._session = requests.Session()
        self._session.headers = {
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }

    def _acquire_access_token_from_refresh_token(self):
        payload = {
            "grant_type": "refresh_token",
            "redirect_uri": self._credentials["redirect_uri"],
            "refresh_token": self._credentials["refresh_token"],
            "client_id": self._credentials["client_id"],
            "client_secret": self._credentials["client_secret"],
        }

        resp = requests.post(self.BASE_URL + "/oauth/v1/token", data=payload)
        if resp.status_code == HTTPStatus.FORBIDDEN:
            raise HubspotInvalidAuth(resp.content, response=resp)

        resp.raise_for_status()
        auth = resp.json()
        self._credentials["access_token"] = auth["access_token"]
        self._credentials["refresh_token"] = auth["refresh_token"]
        self._credentials["token_expires"] = datetime.utcnow() + timedelta(seconds=auth["expires_in"] - 600)
        logger.info(f"Token refreshed. Expires at {self._credentials['token_expires']}")

    @property
    def api_key(self) -> Optional[str]:
        """Get API Key if set"""
        return self._credentials.get("api_key")

    @property
    def access_token(self) -> Optional[str]:
        """Get Access Token if set, refreshes token if needed"""
        if not self._credentials.get("access_token"):
            return None

        if self._credentials["token_expires"] is None or self._credentials["token_expires"] < datetime.utcnow():
            self._acquire_access_token_from_refresh_token()
        return self._credentials.get("access_token")

    def _add_auth(self, params: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """Add auth info to request params/header"""
        params = params or {}

        if self.access_token:
            self._session.headers["Authorization"] = f"Bearer {self.access_token}"
        else:
            params["hapikey"] = self.api_key
        return params

    @staticmethod
    def _parse_and_handle_errors(response) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        """Handle response"""
        message = "Unknown error"
        if response.headers.get("content-type") == "application/json;charset=utf-8" and response.status_code != HTTPStatus.OK:
            message = response.json().get("message")

        if response.status_code == HTTPStatus.FORBIDDEN:
            """ Once hit the forbidden endpoint, we return the error message from response. """
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
    def get(self, url: str, params=None) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        response = self._session.get(self.BASE_URL + url, params=self._add_auth(params))
        return self._parse_and_handle_errors(response)

    def post(self, url: str, data: Mapping[str, Any], params=None) -> Union[Mapping[str, Any], List[Mapping[str, Any]]]:
        response = self._session.post(self.BASE_URL + url, params=self._add_auth(params), json=data)
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

    def list(self, fields) -> Iterable:
        yield from self.read(partial(self._api.get, url=self.url))

    def _filter_dynamic_fields(self, records: Iterable) -> Iterable:
        """Skip certain fields because they are too dynamic and change every call (timers, etc),
        see https://github.com/airbytehq/airbyte/issues/2397
        """
        for record in records:
            if isinstance(record, Mapping) and "properties" in record:
                for key in list(record["properties"].keys()):
                    if key.startswith("hs_time_in"):
                        record["properties"].pop(key)
            yield record

    @staticmethod
    def _cast_value(declared_field_types: List, field_name: str, field_value):

        if field_value is None and "null" in declared_field_types:
            return field_value

        actual_field_type = type(field_value)
        actual_field_type_name = CUSTOM_FIELD_VALUE_TYPE_CAST.get(actual_field_type)
        if actual_field_type_name in declared_field_types:
            return field_value

        target_type_name = next(filter(lambda t: t != "null", declared_field_types))
        target_type = CUSTOM_FIELD_VALUE_TYPE_CAST_REVERSED.get(target_type_name)

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

        if self.entity not in {"contact", "engagement", "product", "quote", "ticket", "company", "deal", "line_item"}:
            return record

        if not record.get("properties"):
            return record

        properties = properties or self.properties

        for field_name, field_value in record["properties"].items():
            declared_field_types = properties[field_name].get("type") or []
            if not isinstance(declared_field_types, Iterable):
                declared_field_types = [declared_field_types]
            record["properties"][field_name] = self._cast_value(declared_field_types, field_name, field_value)

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

    def _read(self, getter: Callable, params: MutableMapping[str, Any] = None) -> Iterator:
        while True:
            response = getter(params=params)
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
                    logger.warn(f"Stream `{self.data_field}` cannot be procced. {response.get('message')}")
                    break

                if response.get(self.data_field) is None:
                    """
                    When the response doen't have the stream's data, raise an exception.
                    """
                    raise RuntimeError("Unexpected API response: {} not in {}".format(self.data_field, response.keys()))

                yield from response[self.data_field]

                # pagination
                if "paging" in response:  # APIv3 pagination
                    if "next" in response["paging"]:
                        params["after"] = response["paging"]["next"]["after"]
                    else:
                        break
                else:
                    if not response.get(self.more_key, False):
                        break
                    if self.page_field in response:
                        params[self.page_filter] = response[self.page_field]
            else:
                response = list(response)
                yield from response

                # pagination
                if len(response) < self.limit:
                    break
                else:
                    params[self.page_filter] = params.get(self.page_filter, 0) + self.limit

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        default_params = {self.limit_field: self.limit, "properties": ",".join(self.properties.keys())}
        params = {**default_params, **params} if params else {**default_params}

        yield from self._filter_dynamic_fields(self._filter_old_records(self._transform(self._read(getter, params))))

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


class IncrementalStream(Stream, ABC):
    """Stream that supports state and incremental read"""

    state_pk = "timestamp"
    limit = 1000

    @property
    @abstractmethod
    def updated_at_field(self):
        """Name of the field associated with the state"""

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return {self.state_pk: str(self._state)}
        return None

    @state.setter
    def state(self, value):
        self._state = pendulum.parse(value[self.state_pk])
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

        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state

    def read_chunked(
        self, getter: Callable, params: Mapping[str, Any] = None, chunk_size: pendulum.duration = pendulum.duration(days=1)
    ) -> Iterator:
        params = {**params} if params else {}
        now_ts = int(pendulum.now().timestamp() * 1000)
        start_ts = int(self._start_date.timestamp() * 1000)
        chunk_size = int(chunk_size.total_seconds() * 1000)

        for ts in range(start_ts, now_ts, chunk_size):
            end_ts = ts + chunk_size
            params["startTimestamp"] = ts
            params["endTimestamp"] = end_ts
            logger.info(
                f"Reading chunk from stream {self.name} between {pendulum.from_timestamp(ts / 1000)} and {pendulum.from_timestamp(end_ts / 1000)}"
            )
            yield from super().read(getter, params)


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

    def __init__(self, entity: str = None, associations: List[str] = None, include_archived_only: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity or self.entity
        self.associations = associations or self.associations
        self._include_archived_only = include_archived_only

        if not self.entity:
            raise ValueError("Entity must be set either on class or instance level")

    def list(self, fields) -> Iterable:
        params = {
            "archived": str(self._include_archived_only).lower(),
            "associations": self.associations,
        }
        generator = self.read(partial(self._api.get, url=self.url), params)
        yield from self._flat_associations(generator)

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

    def list(self, fields) -> Iterable:
        for row in self.read(getter=partial(self._api.get, url=self.url)):
            record = self._api.get(f"/email/public/v1/campaigns/{row['id']}")
            yield {**row, **record}


class ContactListStream(Stream):
    """Contact lists, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/lists/get_lists
    """

    url = "/contacts/v1/lists"
    data_field = "lists"
    more_key = "has-more"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"
    limit_field = "count"


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

    def list(self, fields) -> Iterable:
        params = {"propertiesWithHistory": "dealstage"}
        yield from self.read(partial(self._api.get, url=self.url), params)


class DealStream(CRMObjectStream):
    """Deals, API v3"""

    def __init__(self, **kwargs):
        super().__init__(entity="deal", **kwargs)
        self._stage_history = DealStageHistoryStream(**kwargs)

    def list(self, fields) -> Iterable:
        history_by_id = {}
        for record in self._stage_history.list(fields):
            if all(field in record for field in ("id", "dealstage")):
                history_by_id[record["id"]] = record["dealstage"]
        for record in super().list(fields):
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
    Docs: https://legacydocs.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type
    """

    url = "/crm-pipelines/v1/pipelines/tickets"
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


class EngagementStream(Stream):
    """Engagements, API v1
    Docs: https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements
    """

    entity = "engagement"
    url = "/engagements/v1/engagements/paged"
    more_key = "hasMore"
    limit = 250
    updated_at_field = "lastUpdated"
    created_at_field = "createdAt"

    def _transform(self, records: Iterable) -> Iterable:
        yield from super()._transform({**record.pop("engagement"), **record} for record in records)


class FormStream(Stream):
    """Marketing Forms, API v2
    by default non-marketing forms are filtered out of this endpoint
    Docs: https://developers.hubspot.com/docs/api/marketing/forms
    """

    entity = "form"
    url = "/forms/v2/forms"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


class OwnerStream(Stream):
    """Owners, API v3
    Docs: https://legacydocs.hubspot.com/docs/methods/owners/get_owners
    """

    url = "/crm/v3/owners"
    updated_at_field = "updatedAt"
    created_at_field = "createdAt"


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
