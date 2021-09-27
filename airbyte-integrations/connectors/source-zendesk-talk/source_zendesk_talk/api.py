#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
from abc import ABC, abstractmethod
from functools import partial
from http import HTTPStatus
from typing import Any, Callable, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Union

import backoff
import pendulum as pendulum
import requests
from base_python.entrypoint import logger

from .errors import ZendeskAccessDenied, ZendeskInvalidAuth, ZendeskRateLimited, ZendeskTimeout


def retry_pattern(backoff_type, **wait_gen_kwargs):
    def sleep_on_ratelimit(details):
        _, exc, _ = sys.exc_info()
        logger.info(str(exc))
        logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} more seconds then retrying...")

    def log_giveup(_details):
        logger.error("Max retry limit reached")

    return backoff.on_exception(
        backoff_type,
        (ZendeskRateLimited, ZendeskTimeout),
        jitter=None,
        on_backoff=sleep_on_ratelimit,
        on_giveup=log_giveup,
        **wait_gen_kwargs,
    )


class API:
    """Zendesk Talk API interface, authorize, retrieve and post, supports backoff logic"""

    def __init__(self, subdomain: str, access_token: str, email: str):
        self.BASE_URL = f"https://{subdomain}.zendesk.com/api/v2/channels/voice"
        self._session = requests.Session()
        self._session.headers = {"Content-Type": "application/json"}
        self._session.auth = (f"{email}/token", access_token)

    @staticmethod
    def _parse_and_handle_errors(response) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        """Handle response"""
        message = "Unknown error"
        if response.headers.get("content-type") == "application/json;charset=utf-8" and response.status_code != HTTPStatus.OK:
            message = response.json().get("message")

        if response.status_code == HTTPStatus.FORBIDDEN:
            raise ZendeskAccessDenied(response.text, response=response)
        elif response.status_code == HTTPStatus.UNAUTHORIZED:
            raise ZendeskInvalidAuth(response.text, response=response)
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise ZendeskRateLimited(
                "429 Rate Limit Exceeded: API rate-limit. See https://developer.zendesk.com/rest_api/docs/support/usage_limits",
                response=response,
            )
        elif response.status_code in (HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE):
            raise ZendeskTimeout(message, response=response)
        else:
            response.raise_for_status()

        return response.json()

    @retry_pattern(backoff.expo, max_tries=4, factor=5)
    def get(self, url: str, domain_inclusion=False, params=None) -> Union[MutableMapping[str, Any], List[MutableMapping[str, Any]]]:
        response = self._session.get(url if domain_inclusion else self.BASE_URL + url, params=params or {})
        return self._parse_and_handle_errors(response)


class Stream(ABC):
    """Base class for all streams. Responsible for data fetching and pagination"""

    stream_stats = False
    has_more = "next_page"
    count_field = "count"
    data_field = "results"

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
        if self.stream_stats:
            yield self.read_stats(partial(self._api.get, url=self.url))
        else:
            yield from self.read(partial(self._api.get, url=self.url))

    def _paginator(self, getter: Callable) -> Iterator:
        domain_inclusion = False
        counter = 0
        while True:
            response = getter(domain_inclusion=domain_inclusion)
            if response.get(self.data_field) is None:
                raise RuntimeError("Unexpected API response: {} not in {}".format(self.data_field, response.keys()))

            yield from response[self.data_field]
            counter += len(response[self.data_field])

            if response[self.count_field] <= counter:
                break
            else:
                getter.keywords.update({"url": response[self.has_more], "params": None})
                domain_inclusion = True

    def read_stats(self, getter: Callable) -> Any:
        response = getter()
        return response[self.data_field]

    def read(self, getter: Callable) -> Iterator:
        yield from self._paginator(getter)


class IncrementalStream(Stream, ABC):
    """Stream that supports state and incremental read"""

    state_pk = "timestamp"

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
        for record in self._paginator(getter):
            yield record
            cursor = pendulum.parse(record[self.updated_at_field])
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor

        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state


class PhoneNumbersStream(Stream):
    """Phone Numbers
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers
    """

    url = "/phone_numbers"
    data_field = "phone_numbers"


class AddressesStream(Stream):
    """Addresses
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/phone_numbers#list-phone-numbers
    """

    url = "/addresses"
    data_field = "addresses"


class GreetingCategoriesStream(Stream):
    """Greeting Categories
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greeting-categories
    """

    url = "/greeting_categories"
    data_field = "greeting_categories"


class GreetingsStream(Stream):
    """Greetings
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greetings
    """

    url = "/greetings"
    data_field = "greetings"


class IVRsStream(Stream):
    """IVRs
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs
    """

    url = "/ivr"
    data_field = "ivrs"


class IVRMenusStream(Stream):
    """IVR Menus
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs
    """

    url = "/ivr/{}/menus"
    data_field = "ivr_menus"

    def list(self, fields) -> Iterable:
        ivr_obj = IVRsStream(api=self._api, start_date=str(self._start_date))
        for ivr in ivr_obj.list(fields=[]):
            for ivr_menu in self.read(partial(self._api.get, url=self.url.format(ivr["id"]))):
                yield {"ivr_id": ivr["id"], **ivr_menu}


class IVRRoutesStream(Stream):
    """IVR Routes
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivr_routes#list-ivr-routes
    """

    url = "/ivr/{}/menus/{}/routes"
    data_field = "ivr_routes"

    def list(self, fields) -> Iterable:
        ivr_menu_obj = IVRMenusStream(api=self._api, start_date=str(self._start_date))
        for ivr_menu in ivr_menu_obj.list(fields=[]):
            for ivr_route in self.read(partial(self._api.get, url=self.url.format(ivr_menu["ivr_id"], ivr_menu["id"]))):
                yield {"ivr_id": ivr_menu["ivr_id"], "ivr_menu_id": ivr_menu["id"], **ivr_route}


class AccountOverviewStream(Stream):
    """Account Overview
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-account-overview
    """

    url = "/stats/account_overview"
    data_field = "account_overview"
    stream_stats = True


class AgentsActivityStream(Stream):
    """Agents Activity
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#list-agents-activity
    """

    url = "/stats/agents_activity"
    data_field = "agents_activity"


class AgentsOverviewStream(Stream):
    """Agents Overview
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-agents-overview
    """

    url = "/stats/agents_overview"
    data_field = "agents_overview"
    stream_stats = True


class CurrentQueueActivityStream(Stream):
    """Current Queue Activity
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-current-queue-activity
    """

    url = "/stats/current_queue_activity"
    data_field = "current_queue_activity"
    stream_stats = True


class CallsStream(IncrementalStream):
    """Calls
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-calls-export
    """

    url = "/stats/incremental/calls"
    data_field = "calls"
    updated_at_field = "updated_at"

    def list(self, fields) -> Iterable:
        params = {"start_time": int(self._start_date.timestamp())}
        yield from self.read(partial(self._api.get, url=self.url, params=params))


class CallLegsStream(IncrementalStream):
    """Call Legs
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-call-legs-export
    """

    url = "/stats/incremental/legs"
    data_field = "legs"
    updated_at_field = "updated_at"

    def list(self, fields) -> Iterable:
        params = {"start_time": int(self._start_date.timestamp())}
        yield from self.read(partial(self._api.get, url=self.url, params=params))
