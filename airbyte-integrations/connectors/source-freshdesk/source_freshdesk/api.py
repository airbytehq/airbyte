"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, Iterator, Mapping, MutableMapping, Optional, Sequence

import pendulum
import requests
from base_python.entrypoint import logger  # FIXME (Eugene K): use standard logger
from requests import HTTPError


class FreshdeskError(HTTPError):
    """
    Base error class.
    Subclassing HTTPError to avoid breaking existing code that expects only HTTPErrors.
    """


class FreshdeskBadRequest(FreshdeskError):
    """Most 40X and 501 status codes"""


class FreshdeskUnauthorized(FreshdeskError):
    """401 Unauthorized"""


class FreshdeskAccessDenied(FreshdeskError):
    """403 Forbidden"""


class FreshdeskNotFound(FreshdeskError):
    """404"""


class FreshdeskRateLimited(FreshdeskError):
    """429 Rate Limit Reached"""


class FreshdeskServerError(FreshdeskError):
    """50X errors"""


class API:
    def __init__(self, domain: str, api_key: str, verify: bool = True, proxies: MutableMapping[str, str] = None):
        """Basic HTTP interface to read from endpoints"""
        self._api_prefix = f"https://{domain.rstrip('/')}/api/v2/"
        self._session = requests.Session()
        self._session.auth = (api_key, "unused_with_api_key")
        self._session.verify = verify
        self._session.proxies = proxies
        self._session.headers = {"Content-Type": "application/json"}

        if domain.find("freshdesk.com") < 0:
            raise AttributeError("Freshdesk v2 API works only via Freshdesk domains and not via custom CNAMEs")

    @staticmethod
    def _parse_and_handle_errors(req):
        try:
            j = req.json()
        except ValueError:
            j = {}

        error_message = "Freshdesk Request Failed"
        if "errors" in j:
            error_message = "{}: {}".format(j.get("description"), j.get("errors"))
        # API docs don't mention this clearly, but in the case of bad credentials the returned JSON will have a
        # "message"  field at the top level
        elif "message" in j:
            error_message = j["message"]

        if req.status_code == 400:
            raise FreshdeskBadRequest(error_message)
        elif req.status_code == 401:
            raise FreshdeskUnauthorized(error_message)
        elif req.status_code == 403:
            raise FreshdeskAccessDenied(error_message)
        elif req.status_code == 404:
            raise FreshdeskNotFound(error_message)
        elif req.status_code == 429:
            raise FreshdeskRateLimited(
                "429 Rate Limit Exceeded: API rate-limit has been reached until {} seconds. See "
                "http://freshdesk.com/api#ratelimit".format(req.headers.get("Retry-After"))
            )
        elif 500 <= req.status_code < 600:
            raise FreshdeskServerError("{}: Server Error".format(req.status_code))

        # Catch any other errors
        try:
            req.raise_for_status()
        except HTTPError as e:
            raise FreshdeskError("{}: {}".format(e, j))

        return j

    def get(self, url: str, params: Mapping = None):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        for _ in range(10):
            params = params or {}
            response = self._session.get(self._api_prefix + url, params=params)
            try:
                return self._parse_and_handle_errors(response)
            except FreshdeskRateLimited:
                retry_after = int(response.headers["Retry-After"])
                logger.info(f"Rate limit reached. Sleeping for {retry_after} seconds")
                time.sleep(retry_after + 1)  # extra second to cover any fractions of second
        raise Exception("Max retry limit reached")


class StreamAPI(ABC):
    """Basic stream API that allows to iterate over entities"""

    result_return_limit = 100  # maximum value
    maximum_page = 500  # see https://developers.freshdesk.com/api/#best_practices

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Read using getter"""
        params = params or {}
        for page in range(1, self.maximum_page):
            batch = list(getter(params={**params, "per_page": self.result_return_limit, "page": page}))
            yield from batch

            if len(batch) < self.result_return_limit:
                break


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
        yield from self.read(partial(self._api.get, url="agents"))


class CompaniesAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="companies"))


class ContactsAPI(IncrementalStreamAPI):
    state_filter = "_updated_since"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="contacts"))


class GroupsAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="groups"))


class RolesAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="roles"))


class SkillsAPI(ClientIncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="skills"))


class SurveysAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="surveys"))


class TicketsAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        params = {"include": "description"}
        yield from self.read(partial(self._api.get, url="tickets"), params=params)


class TimeEntriesAPI(ClientIncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="time_entries"))


class ConversationsAPI(ClientIncrementalStreamAPI):
    """Notes and Replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        tickets = TicketsAPI(self._api)
        if self.state:
            tickets.state = self.state
        for ticket in tickets.list():
            url = f"tickets/{ticket['id']}/conversations"
            yield from self.read(partial(self._api.get, url=url))


class SatisfactionRatingsAPI(ClientIncrementalStreamAPI):
    """Surveys satisfaction replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="surveys/satisfaction_ratings"))
