#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib import parse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from requests.auth import AuthBase
from source_freshdesk.utils import CallCredit


class FreshdeskStream(HttpStream, ABC):
    """Basic stream API that allows to iterate over entities"""

    call_credit = 1  # see https://developers.freshdesk.com/api/#embedding
    result_return_limit = 100
    primary_key = "id"
    link_regex = re.compile(r'<(.*?)>;\s*rel="next"')

    def __init__(self, authenticator: AuthBase, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(authenticator=authenticator)
        requests_per_minute = config.get("requests_per_minute")
        self.domain = config["domain"]
        self._call_credit = CallCredit(balance=requests_per_minute) if requests_per_minute else None
        # By default, only tickets that have been created within the past 30 days will be returned.
        # Since this logic rely not on updated tickets, it can break tickets dependant streams - conversations.
        # So updated_since parameter will be always used in tickets streams. And start_date will be used too
        # with default value 30 days look back.
        self.start_date = (
            pendulum.parse(config.get("start_date")) if config.get("start_date") else pendulum.now() - pendulum.duration(days=30)
        )

    @property
    def url_base(self) -> str:
        return parse.urljoin(f"https://{self.domain.rstrip('/')}", "/api/v2")

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code == requests.codes.too_many_requests:
            return float(response.headers.get("Retry-After", 0))

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        link_header = response.headers.get("Link")
        if not link_header:
            return {}
        match = self.link_regex.search(link_header)
        next_url = match.group(1)
        params = parse.parse_qs(parse.urlparse(next_url).query)
        return self.parse_link_params(link_query_params=params)

    def parse_link_params(self, link_query_params: Mapping[str, List[str]]) -> Mapping[str, Any]:
        return {"per_page": link_query_params["per_page"][0], "page": link_query_params["page"][0]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.result_return_limit}
        if next_page_token and "page" in next_page_token:
            params["page"] = next_page_token["page"]
        return params

    def _consume_credit(self, credit):
        """Consume call credit, if there is no credit left within current window will sleep til next period"""
        if self._call_credit:
            self._call_credit.consume(credit)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self._consume_credit(self.call_credit)
        yield from super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        return data if data else []


class IncrementalFreshdeskStream(FreshdeskStream, IncrementalMixin):

    cursor_filter = "updated_since"  # Name of filter that corresponds to the state
    state_checkpoint_interval = 100

    def __init__(self, authenticator: AuthBase, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(authenticator=authenticator, config=config, *args, **kwargs)
        self._cursor_value = ""

    @property
    def cursor_field(self) -> str:
        return "updated_at"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_field: self._cursor_value} if self._cursor_value else {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, self.start_date)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params[self.cursor_filter] = stream_state.get(self.cursor_field, self.start_date)
        return params

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield record
            self._cursor_value = max(record[self.cursor_field], self._cursor_value)


class Agents(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "agents"


class Companies(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "companies"


class Contacts(IncrementalFreshdeskStream):
    cursor_filter = "_updated_since"

    def path(self, **kwargs) -> str:
        return "contacts"


class Groups(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "groups"


class Roles(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "roles"


class Skills(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "skills"


class TimeEntries(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "time_entries"


class Surveys(FreshdeskStream):
    def path(self, **kwargs) -> str:
        return "surveys"


class Tickets(IncrementalFreshdeskStream):
    ticket_paginate_limit = 300
    call_credit = 3  # each include consumes 2 additional credits
    use_cache = True

    def path(self, **kwargs) -> str:
        return "tickets"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        includes = ["description", "requester", "stats"]
        params.update(
            {"order_type": "asc", "order_by": self.cursor_field, "include": ",".join(includes)}  # ASC order, to get the old records first
        )
        if next_page_token and self.cursor_filter in next_page_token:
            params[self.cursor_filter] = next_page_token[self.cursor_filter]
        return params

    def parse_link_params(self, link_query_params: Mapping[str, List[str]]) -> Mapping[str, Any]:
        params = super().parse_link_params(link_query_params)
        if self.cursor_filter in link_query_params:
            params[self.cursor_filter] = link_query_params[self.cursor_filter][0]
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This block extends Incremental stream to overcome '300 page' server error.
        Since the Ticket endpoint has a 300 page pagination limit, after 300 pages, update the parameters with
        query using 'updated_since' = last_record, if there is more data remaining.
        """
        next_page_token = super().next_page_token(response=response)

        if next_page_token and int(next_page_token["page"]) > self.ticket_paginate_limit:
            # get last_record from latest batch, pos. -1, because of ACS order of records
            last_record_updated_at = response.json()[-1]["updated_at"]
            last_record_updated_at = pendulum.parse(last_record_updated_at)
            # updating request parameters with last_record state
            next_page_token[self.cursor_filter] = last_record_updated_at
            next_page_token.pop("page")

        return next_page_token


class Conversations(FreshdeskStream):
    """Notes and Replies"""

    def __init__(self, authenticator: AuthBase, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(authenticator=authenticator, config=config, args=args, kwargs=kwargs)
        self.tickets_stream = Tickets(authenticator=authenticator, config=config)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"tickets/{stream_slice['id']}/conversations"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for ticket in self.tickets_stream.read_records(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice={}, stream_state={}
        ):
            yield {"id": ticket["id"]}


class SatisfactionRatings(IncrementalFreshdeskStream):
    cursor_filter = "created_since"

    def path(self, **kwargs) -> str:
        return "surveys/satisfaction_ratings"
