#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib import parse

import pendulum
import requests
import re
from airbyte_cdk.entrypoint import logger  # FIXME (Eugene K): use standard logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.sentry import AirbyteSentry
from requests.auth import AuthBase
from source_freshdesk.utils import CallCredit


LINK_REGEX = re.compile(r'<(.*?)>;\s*rel="next"')


class FreshdeskStream(HttpStream, ABC):
    """Basic stream API that allows to iterate over entities"""
    call_credit = 1  # see https://developers.freshdesk.com/api/#embedding
    primary_key = "id"

    def __init__(self, authenticator: AuthBase, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(authenticator=authenticator)
        requests_per_minute = config["requests_per_minute"]
        start_date = config["start_date"]
        self.domain = config["domain"]
        self._call_credit = CallCredit(balance=requests_per_minute) if requests_per_minute else None
        # By default, only tickets that have been created within the past 30 days will be returned.
        # Since this logic rely not on updated tickets, it can break tickets dependant streams - conversations.
        # So updated_since parameter will be always used in tickets streams. And start_date will be used too
        # with default value 30 days look back.
        self.start_date = pendulum.parse(start_date) if start_date else pendulum.now() - pendulum.duration(days=30)
    
    @property
    def url_base(self) -> str:
        return f"https://{self.domain.rstrip('/')}/api/v2"
    
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code == requests.codes.too_many_requests:
            return float(response.headers.get("Retry-After"))

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "Airbyte",
        }
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            link_header = response.headers.get("Link")
            if not link_header:
                return {}
            match = LINK_REGEX.search(link_header)
            next_url = match.group(1)
            params = parse.parse_qs(parse.urlparse(next_url).query)
            return {"per_page": params['per_page'][0], "page": params['page'][0]}
        except Exception as e:
            raise KeyError(f"error parsing next_page token: {e}")
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": 100}
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
        yield from super().read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        if not data:
            return
        for element in data:
            yield element


class IncrementalFreshdeskStream(FreshdeskStream, ABC):

    @property
    def cursor_field(self) -> str:
        return "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        current_stream_state_date = current_stream_state.get("updated_at", self.start_date)
        if isinstance(current_stream_state_date, str):
            current_stream_state_date = pendulum.parse(current_stream_state_date)
        latest_record_date = pendulum.parse(latest_record.get("updated_at")) if latest_record.get("updated_at") else self.start_date

        return {"updated_at": max(current_stream_state_date, latest_record_date)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if "updated_at" in stream_state:
            params[self.state_filter] = stream_state["updated_at"]
        else:
            params[self.state_filter] = self.start_date
        return params


class Agents(FreshdeskStream):

    def path(self, **kwargs) -> str:
        return "agents"


class Companies(FreshdeskStream):

    def path(self, **kwargs) -> str:
        return "companies"


class Contacts(IncrementalFreshdeskStream):
    state_filter = "_updated_since"

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


class Tickets(IncrementalFreshdeskStream):
    state_filter = "updated_since"
    ticket_paginate_limit = 300

    def path(self, **kwargs) -> str:
        return "tickets"
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if next_page_token and "updated_since" in next_page_token:
            params["updated_since"] = next_page_token["updated_since"]
        return params
    
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Read ticket records

        This block extends Incremental stream to overcome '300 page' server error.
        Since the Ticket endpoint has a 300 page pagination limit, after 300 pages, update the parameters with
        query using 'updated_since' = last_record, if there is more data remaining.
        """
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
        page = 1
        with AirbyteSentry.start_transaction("read_records", self.name), AirbyteSentry.start_transaction_span("read_records"):
            while not pagination_complete:
                request_headers = self.request_headers(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
                )
                request = self._create_prepared_request(
                    path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                    headers=dict(request_headers, **self.authenticator.get_auth_header()),
                    params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                    json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                    data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                )
                response = self._send_request(request, {})
                tickets = response.json()
                yield from tickets

                next_page_token = self.next_page_token(response)
                # checkpoint & switch the pagination
                if page == self.ticket_paginate_limit and next_page_token:
                    # get last_record from latest batch, pos. -1, because of ACS order of records
                    last_record_updated_at = tickets[-1]["updated_at"]
                    page = 0  # reset page counter
                    last_record_updated_at = pendulum.parse(last_record_updated_at)
                    # updating request parameters with last_record state
                    next_page_token["updated_since"] = last_record_updated_at
                # Increment page
                page += 1

                if not next_page_token:
                    pagination_complete = True

            # Always return an empty generator just in case no records were ever yielded
            yield from []


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
            yield {'id': ticket['id']}


class SatisfactionRatings(IncrementalFreshdeskStream):
    state_filter = "created_since"

    def path(self, **kwargs) -> str:
        return "surveys/satisfaction_ratings"
