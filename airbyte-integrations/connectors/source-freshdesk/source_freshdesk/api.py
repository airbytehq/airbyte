#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, Iterator, Mapping, MutableMapping, Optional, Sequence

import pendulum
import requests
from base_python.entrypoint import logger  # FIXME (Eugene K): use standard logger
from requests import HTTPError
from source_freshdesk.errors import (
    FreshdeskAccessDenied,
    FreshdeskBadRequest,
    FreshdeskError,
    FreshdeskNotFound,
    FreshdeskRateLimited,
    FreshdeskServerError,
    FreshdeskUnauthorized,
)
from source_freshdesk.utils import CallCredit, retry_after_handler, retry_connection_handler


class API:
    def __init__(
        self,
        domain: str,
        api_key: str,
        requests_per_minute: int = None,
        verify: bool = True,
        proxies: MutableMapping[str, Any] = None,
    ):
        """Basic HTTP interface to read from endpoints"""
        self._api_prefix = f"https://{domain.rstrip('/')}/api/v2/"
        self._session = requests.Session()
        self._session.auth = (api_key, "unused_with_api_key")
        self._session.verify = verify
        self._session.proxies = proxies
        self._session.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Airbyte",
        }

        self._call_credit = CallCredit(balance=requests_per_minute) if requests_per_minute else None

        if domain.find("freshdesk.com") < 0:
            raise AttributeError("Freshdesk v2 API works only via Freshdesk domains and not via custom CNAMEs")

    @staticmethod
    def _parse_and_handle_errors(response):
        try:
            body = response.json()
        except ValueError:
            body = {}

        error_message = "Freshdesk Request Failed"
        if "errors" in body:
            error_message = f"{body.get('description')}: {body['errors']}"
        # API docs don't mention this clearly, but in the case of bad credentials the returned JSON will have a
        # "message"  field at the top level
        elif "message" in body:
            error_message = f"{body.get('code')}: {body['message']}"

        if response.status_code == 400:
            raise FreshdeskBadRequest(error_message or "Wrong input, check your data", response=response)
        elif response.status_code == 401:
            raise FreshdeskUnauthorized(error_message or "Invalid credentials", response=response)
        elif response.status_code == 403:
            raise FreshdeskAccessDenied(error_message or "You don't have enough permissions", response=response)
        elif response.status_code == 404:
            raise FreshdeskNotFound(error_message or "Resource not found", response=response)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise FreshdeskRateLimited(
                f"429 Rate Limit Exceeded: API rate-limit has been reached until {retry_after} seconds."
                " See http://freshdesk.com/api#ratelimit",
                response=response,
            )
        elif 500 <= response.status_code < 600:
            raise FreshdeskServerError(f"{response.status_code}: Server Error", response=response)

        # Catch any other errors
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise FreshdeskError(f"{err}: {body}", response=response) from err

        return body

    @retry_connection_handler(max_tries=5, factor=5)
    @retry_after_handler(max_tries=3)
    def get(self, url: str, params: Mapping = None):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        params = params or {}
        response = self._session.get(self._api_prefix + url, params=params)
        return self._parse_and_handle_errors(response)

    def consume_credit(self, credit):
        """Consume call credit, if there is no credit left within current window will sleep til next period"""
        if self._call_credit:
            self._call_credit.consume(credit)


class StreamAPI(ABC):
    """Basic stream API that allows to iterate over entities"""

    result_return_limit = 100  # maximum value
    maximum_page = 500  # see https://developers.freshdesk.com/api/#best_practices
    call_credit = 1  # see https://developers.freshdesk.com/api/#embedding

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    def _api_get(self, url: str, params: Mapping = None):
        """Wrapper around API GET method to respect call rate limit"""
        self._api.consume_credit(self.call_credit)
        return self._api.get(url, params=params)

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Read using getter"""
        params = params or {}

        for page in range(1, self.maximum_page):
            batch = list(
                getter(
                    params={
                        **params,
                        "per_page": self.result_return_limit,
                        "page": page,
                    }
                )
            )
            yield from batch

            if len(batch) < self.result_return_limit:
                return iter(())


class IncrementalStreamAPI(StreamAPI, ABC):
    state_pk = "updated_at"  # Name of the field associated with the state
    state_filter = "updated_since"  # Name of filter that corresponds to the state

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return {self.state_pk: str(self._state)}
        return None

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = pendulum.parse(value[self.state_pk])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state: Optional[Mapping[str, Any]] = None

    def _state_params(self) -> Mapping[str, Any]:
        """Build query parameters responsible for current state"""
        if self._state:
            return {self.state_filter: self._state}
        return {}

    @property
    def name(self):
        """Name of the stream"""
        stream_name = self.__class__.__name__
        if stream_name.endswith("API"):
            stream_name = stream_name[:-3]
        return stream_name

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Read using getter, patched to respect current state"""
        params = params or {}
        params = {**params, **self._state_params()}
        latest_cursor = None
        for record in super().read(getter, params):
            cursor = pendulum.parse(record[self.state_pk])
            # filter out records older then state
            if self._state and self._state >= cursor:
                continue
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record

        if latest_cursor:
            logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
            self._state = max(latest_cursor, self._state) if self._state else latest_cursor


class ClientIncrementalStreamAPI(IncrementalStreamAPI, ABC):
    """Incremental stream that don't have native API support, i.e we filter on the client side only"""

    def _state_params(self) -> Mapping[str, Any]:
        """Build query parameters responsible for current state, override because API doesn't support this"""
        return {}


class AgentsAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="agents"))


class CompaniesAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="companies"))


class ContactsAPI(IncrementalStreamAPI):
    state_filter = "_updated_since"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="contacts"))


class GroupsAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="groups"))


class RolesAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="roles"))


class SkillsAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="skills"))


class SurveysAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="surveys"))


class TicketsAPI(IncrementalStreamAPI):
    call_credit = 3  # each include consumes 2 additional credits

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        params = {"include": "description"}
        yield from self.read(partial(self._api_get, url="tickets"), params=params)

    @staticmethod
    def get_tickets(
        result_return_limit: int, getter: Callable, params: Mapping[str, Any] = None, ticket_paginate_limit: int = 300
    ) -> Iterator:
        """
        Read using getter

        This block extends TicketsAPI Stream to overcome '300 page' server error.
        Since the TicketsAPI Stream list has a 300 page pagination limit, after 300 pages, update the parameters with
        query using 'updated_since' = last_record, if there is more data remaining.
        """
        params = params or {}

        # Start page
        page = 1
        # Initial request parameters
        params = {
            **params,
            "order_type": "asc",  # ASC order, to get the old records first
            "order_by": "updated_at",
            "per_page": result_return_limit,
        }

        while True:
            params["page"] = page
            batch = list(getter(params=params))
            yield from batch

            if len(batch) < result_return_limit:
                return iter(())

            # checkpoint & switch the pagination
            if page == ticket_paginate_limit:
                # get last_record from latest batch, pos. -1, because of ACS order of records
                last_record_updated_at = batch[-1]["updated_at"]
                page = 0  # reset page counter
                last_record_updated_at = pendulum.parse(last_record_updated_at)
                # updating request parameters with last_record state
                params["updated_since"] = last_record_updated_at
                # Increment page
            page += 1

    # Override the super().read() method with modified read for tickets
    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Read using getter, patched to respect current state"""
        params = params or {}
        params = {**params, **self._state_params()}
        latest_cursor = None
        for record in self.get_tickets(self.result_return_limit, getter, params):
            cursor = pendulum.parse(record[self.state_pk])
            # filter out records older then state
            if self._state and self._state >= cursor:
                continue
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record

        if latest_cursor:
            logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
            self._state = max(latest_cursor, self._state) if self._state else latest_cursor


class TimeEntriesAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="time_entries"))


class ConversationsAPI(ClientIncrementalStreamAPI):
    """Notes and Replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        tickets = TicketsAPI(self._api)
        if self.state:
            tickets.state = self.state
        for ticket in tickets.list():
            url = f"tickets/{ticket['id']}/conversations"
            yield from self.read(partial(self._api_get, url=url))


class SatisfactionRatingsAPI(ClientIncrementalStreamAPI):
    """Surveys satisfaction replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api_get, url="surveys/satisfaction_ratings"))
