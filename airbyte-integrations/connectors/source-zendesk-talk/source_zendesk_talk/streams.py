#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

import pendulum as pendulum
import requests
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream


class ZendeskTalkStream(HttpStream, ABC):
    """Base class for streams"""

    primary_key = "id"

    def __init__(self, subdomain: str, **kwargs):
        """Constructor, accepts subdomain to calculate correct url"""
        super().__init__(**kwargs)
        self._subdomain = subdomain

    @property
    @abstractmethod
    def data_field(self) -> str:
        """Specifies root object name in a stream response"""

    @property
    def url_base(self) -> str:
        """API base url based on configured subdomain"""
        return f"https://{self._subdomain}.zendesk.com/api/v2/channels/voice/"

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        response_json = response.json()
        next_page_url = response_json.get("next_page")
        if next_page_url:
            next_url = urlparse(next_page_url)
            next_params = parse_qs(next_url.query)
            return next_params

        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """Usually contains common params e.g. pagination size etc."""
        return dict(next_page_token or {})

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Simply parse json and iterates over root object"""
        response_json = response.json()
        if self.data_field:
            response_json = response_json[self.data_field]

        if not isinstance(response_json, list):
            response_json = [response_json]

        yield from response_json


class ZendeskTalkIncrementalStream(ZendeskTalkStream, ABC):
    """Stream that supports state and incremental read, for now only incremental export endpoints use this class.
    Docs: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports
    """

    # required to support old format as well (only read, but save as new)
    legacy_cursor_field = "timestamp"
    cursor_field = "updated_at"
    filter_param = "start_time"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_state = current_stream_state.get(self.cursor_field, current_stream_state.get(self.legacy_cursor_field))
        new_cursor_value = max(latest_record[self.cursor_field], latest_state or latest_record[self.cursor_field])
        return {self.cursor_field: new_cursor_value}

    def request_params(self, stream_state=None, **kwargs):
        """Add incremental parameters"""
        params = super().request_params(stream_state=stream_state, **kwargs)

        if self.filter_param not in params:
            # use cursor as filter value only if it is not already a parameter (i.e. we are in the middle of the pagination)
            stream_state = stream_state or {}
            state_str = stream_state.get(self.cursor_field, stream_state.get(self.legacy_cursor_field))
            state = pendulum.parse(state_str) if state_str else self._start_date
            params[self.filter_param] = max(state, self._start_date).int_timestamp

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        next_params = super().next_page_token(response)
        if not next_params:
            return None

        current_url = urlparse(response.request.url)
        current_params = parse_qs(current_url.query)

        # check if cursor value was changed
        if current_params[self.filter_param] != next_params[self.filter_param]:
            return next_params

        return None


class ZendeskTalkSingleRecordStream(ZendeskTalkStream, ABC):
    primary_key = "current_timestamp"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record["current_timestamp"] = pendulum.now().int_timestamp
            yield record


class PhoneNumbers(ZendeskTalkStream):
    """Phone Numbers
    Docs: https://developer.zendesk.com/api-reference/voice/talk-api/phone_numbers/#list-phone-numbers
    """

    data_field = "phone_numbers"

    def path(self, **kwargs) -> str:
        return "phone_numbers"


class Addresses(ZendeskTalkStream):
    """Addresses
    Docs: https://developer.zendesk.com/api-reference/voice/talk-api/addresses/#list-addresses
    """

    data_field = "addresses"

    def path(self, **kwargs) -> str:
        return "addresses"


class GreetingCategories(ZendeskTalkStream):
    """Greeting Categories
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greeting-categories
    """

    data_field = "greeting_categories"

    def path(self, **kwargs) -> str:
        return "greeting_categories"


class Greetings(ZendeskTalkStream):
    """Greetings
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/greetings#list-greetings
    """

    data_field = "greetings"

    def path(self, **kwargs) -> str:
        return "greetings"


class IVRs(ZendeskTalkStream):
    """IVRs
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs
    """

    name = "ivrs"
    data_field = "ivrs"
    use_cache = True
    cache_filename = "ivrs.yml"

    def path(self, **kwargs) -> str:
        return "ivr.json"


class IVRMenus(IVRs):
    """IVR Menus
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivrs#list-ivrs
    """

    name = "ivr_menus"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Simply parse json and iterates over root object"""
        ivrs = super().parse_response(response=response, **kwargs)
        for ivr in ivrs:
            for menu in ivr["menus"]:
                yield {"ivr_id": ivr["id"], **menu}


class IVRRoutes(IVRs):
    """IVR Routes
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/ivr_routes#list-ivr-routes
    """

    name = "ivr_routes"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """Simply parse json and iterates over root object"""
        ivrs = super().parse_response(response=response, **kwargs)
        for ivr in ivrs:
            for menu in ivr["menus"]:
                for route in ivr["menus"]:
                    yield {"ivr_id": ivr["id"], "ivr_menu_id": menu["id"], **route}


class AccountOverview(ZendeskTalkSingleRecordStream):
    """Account Overview
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-account-overview
    """

    data_field = "account_overview"

    def path(self, **kwargs) -> str:
        return "stats/account_overview"


class AgentsActivity(ZendeskTalkStream):
    """Agents Activity
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#list-agents-activity
    """

    data_field = "agents_activity"
    primary_key = "agent_id"

    def path(self, **kwargs) -> str:
        return "stats/agents_activity"


class AgentsOverview(ZendeskTalkSingleRecordStream):
    """Agents Overview
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-agents-overview
    """

    data_field = "agents_overview"

    def path(self, **kwargs) -> str:
        return "stats/agents_overview"


class CurrentQueueActivity(ZendeskTalkSingleRecordStream):
    """Current Queue Activity
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/stats#show-current-queue-activity
    """

    data_field = "current_queue_activity"

    def path(self, **kwargs) -> str:
        return "stats/current_queue_activity"


class Calls(ZendeskTalkIncrementalStream):
    """Calls
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-calls-export
    """

    data_field = "calls"
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "stats/incremental/calls"


class CallLegs(ZendeskTalkIncrementalStream):
    """Call Legs
    Docs: https://developer.zendesk.com/rest_api/docs/voice-api/incremental_exports#incremental-call-legs-export
    """

    data_field = "legs"
    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "stats/incremental/legs"
