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

from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, Iterator, Mapping, MutableMapping, Sequence

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
        elif 500 < req.status_code < 600:
            raise FreshdeskServerError("{}: Server Error".format(req.status_code))

        # Catch any other errors
        try:
            req.raise_for_status()
        except HTTPError as e:
            raise FreshdeskError("{}: {}".format(e, j))

        return j

    def get(self, url: str, params: Mapping = None):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        params = params or {}
        req = self._session.get(self._api_prefix + url, params=params)
        return self._parse_and_handle_errors(req)


class StreamAPI(ABC):
    """Basic stream API that allows to iterate over entities"""

    result_return_limit = 100  # maximum value

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""

    def read(self, getter: Callable, params: Mapping[str, Any] = None) -> Iterator:
        """Read using getter"""
        params = params or {}
        pagination_params = dict(per_page=self.result_return_limit, page=1)

        while True:
            batch = list(getter(params={**params, **pagination_params}))
            yield from batch

            if len(batch) < self.result_return_limit:
                break

            pagination_params["page"] += 1


class IncrementalStreamAPI(StreamAPI, ABC):
    @property
    def state_pk(self):
        """Name of the field associated with the state"""
        return "updated_at"

    @property
    def state(self):
        return {self.state_pk: str(self._state)}

    @state.setter
    def state(self, value):
        self._state = pendulum.parse(value[self.state_pk])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    def _state_params(self) -> Mapping[str, Any]:
        """Build query parameters responsible for current state"""
        if self._state:
            return {"updated_since": self._state}
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


class AgentsAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="agents"))


class CompaniesAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="companies"))


class ContactsAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="contacts"))


class GroupsAPI(IncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="groups"))


class RolesAPI(IncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="roles"))


class SkillsAPI(IncrementalStreamAPI):
    """Only users with admin privileges can access the following APIs."""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="skills"))


class SurveysAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="surveys"))


class TicketsAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        params = {"include": "description"}
        yield from self.read(partial(self._api.get, url="tickets"), params=params)


class TimeEntriesAPI(IncrementalStreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="time_entries"))


class ConversationsAPI(StreamAPI):
    """Notes and Replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        for ticket in TicketsAPI(self._api).list():
            url = f"tickets/{ticket['id']}/conversations"
            yield from self.read(partial(self._api.get, url=url))


class SatisfactionRatingsAPI(IncrementalStreamAPI):
    """Surveys satisfaction replies"""

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""
        yield from self.read(partial(self._api.get, url="surveys/satisfaction_ratings"))
