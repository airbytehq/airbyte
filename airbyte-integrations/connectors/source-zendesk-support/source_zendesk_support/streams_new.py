#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import calendar
import time
from abc import ABC
from collections import deque
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from concurrent.futures._base import FINISHED
from datetime import datetime
from functools import partial
from math import ceil
from pickle import PickleError, dumps
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urljoin, urlparse

import pendulum
import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from requests_futures.sessions import PICKLE_ERROR, FuturesSession

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LAST_END_TIME_KEY = "_last_end_time"


class SourceZendeskSupportFuturesSession(FuturesSession):
    def send_future(self, request: requests.PreparedRequest, **kwargs) -> Future:
        if self.session:
            func = self.session.send
        else:
            # avoid calling super to not break pickled method
            func = partial(requests.Session.send, self)

        if isinstance(self.executor, ProcessPoolExecutor):
            # verify function can be pickled
            try:
                dumps(func)
            except (TypeError, PickleError):
                raise RuntimeError(PICKLE_ERROR)

        return self.executor.submit(func, request, **kwargs)


class SourceZendeskSupportStream(HttpStream, ABC):
    """Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    created_at_field = "created_at"
    updated_at_field = "updated_at"
    cursor_field = "updated_at"

    response_list_name = None
    parent = None
    future_requests = None

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, subdomain: str, start_date: str, authenticator: Union[AuthBase, HttpAuthenticator] = None, **kwargs):
        self._start_date = start_date
        super().__init__(**kwargs)
        self._session = SourceZendeskSupportFuturesSession()
        self._session.auth = authenticator

        # add the custom value for generation of a zendesk domain
        self._subdomain = subdomain
        self.future_requests = deque()

    def get_api_records_count(self, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None):
        """
        Count stream records before generating the future requests
        to then correctly generate the pagination parameters.
        """

        count_url = urljoin(self.url_base, f"{self.path(stream_state=stream_state, stream_slice=stream_slice)}/count.json")

        start_date = self._start_date
        params = {}
        if self.cursor_field:
            start_date = stream_state.get(self.cursor_field)
        if start_date:
            params["start_time"] = self.str2datetime(start_date)

        response = self._session.request("get", count_url, params=params).result()
        records_count = response.json().get("count", {}).get("value", 0)

        return records_count

    def generate_future_requests(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ):
        records_count = self.get_api_records_count(stream_slice=stream_slice, stream_state=stream_state)

        page_count = ceil(records_count / self.page_size)
        next_page_token = None
        for page_number in range(1, page_count + 1):
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            params["page"] = page_number
            request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

            request = self._create_prepared_request(
                path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=params,
                json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            )

            request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            # self.future_requests.append(self._send_request(request, request_kwargs))
            self.future_requests.append(
                {
                    "future": self._send_request(request, request_kwargs),
                    "request": request,
                    "request_kwargs": request_kwargs,
                    "retries": 0,
                    "backoff_time": None,
                }
            )

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        response: requests.Response = self._session.send_future(request, **request_kwargs)
        return response

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        return self._send(request, request_kwargs)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.generate_future_requests(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)

        while len(self.future_requests) > 0:
            item = self.future_requests.popleft()

            if self.use_cache:
                # use context manager to handle and store cassette metadata
                with self.cache_file as cass:
                    self.cassete = cass
                    # vcr tries to find records based on the request, if such records exist, return from cache file
                    # else make a request and save record in cache file
                    response = item["future"].result()

                    curr = pendulum.now()
                    request_time = curr - response.elapsed
                    response_time = curr
                    with open(
                        "/Users/hevlich/zazmic/airbyte/airbyte-integrations/connectors/source-zendesk-support/request_response_time_log6.txt",
                        "a+",
                    ) as f:
                        f.write(f"{response.url},{request_time.isoformat()},{response_time.isoformat()}\n")

            else:
                response = item["future"].result()

            if self.should_retry(response):
                if item["retries"] == self.max_retries:
                    print(f"Error {self.future_requests}")
                else:
                    backoff_time = self.backoff_time(response)
                    self.future_requests.append(
                        {
                            "future": self._send_request(item["request"], item["request_kwargs"]),
                            "request": item["request"],
                            "request_kwargs": item["request_kwargs"],
                            "retries": item["retries"] + 1,
                            "backoff_time": backoff_time,
                        }
                    )

            # print("Response: ", item["future"].result().json())
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    @staticmethod
    def _parse_next_page_number(response: requests.Response) -> Optional[int]:
        """Parses a response and tries to find next page number"""
        next_page = response.json().get("next_page")
        if next_page:
            return dict(parse_qsl(urlparse(next_page).query)).get("page")
        return None

    def backoff_time(self, response: requests.Response) -> Union[int, float]:
        """
        The rate limit is 700 requests per minute
        # monitoring-your-request-activity
        See https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/
        The response has a Retry-After header that tells you for how many seconds to wait before retrying.
        """

        retry_after = int(response.headers.get("Retry-After", 0))
        if retry_after and retry_after > 0:
            return int(retry_after)

        # the header X-Rate-Limit returns a amount of requests per minute
        # we try to wait twice as long
        rate_limit = float(response.headers.get("X-Rate-Limit", 0))
        if rate_limit and rate_limit > 0:
            return (60.0 / rate_limit) * 2
        return super().backoff_time(response)

    @staticmethod
    def str2datetime(str_dt: str) -> datetime:
        """convert string to datetime object
        Input example: '2021-07-22T06:55:55Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        if not str_dt:
            return None
        return datetime.strptime(str_dt, DATETIME_FORMAT)

    @staticmethod
    def datetime2str(dt: datetime) -> str:
        """convert datetime object to string
        Output example: '2021-07-22T06:55:55Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        return datetime.strftime(dt.replace(tzinfo=pytz.UTC), DATETIME_FORMAT)

    @staticmethod
    def str2unixtime(str_dt: str) -> Optional[int]:
        """convert string to unixtime number
        Input example: '2021-07-22T06:55:55Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
        Output example: 1626936955"
        """
        if not str_dt:
            return None
        dt = datetime.strptime(str_dt, DATETIME_FORMAT)
        return calendar.timegm(dt.utctimetuple())

    def path(self, **kwargs):
        return self.name

    def next_page_token(self, *args, **kwargs):
        return None

    def parse_response(self, response: requests.Response, **kwargs):
        yield from response.json().get(self.response_list_name or self.name)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """Need to save a cursor values as integer"""
        state = super().get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)
        if state and state.get(self.cursor_field):
            state[self.cursor_field] = int(state[self.cursor_field])
        return state


class Users(SourceZendeskSupportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Organizations(SourceZendeskSupportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Tickets(SourceZendeskSupportStream):
    """Tickets stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""

    # The API compares the start_time with the ticket's generated_timestamp value, not its updated_at value.
    # The generated_timestamp value is updated for all entity updates, including system updates.
    # If a system update occurs after a event, the unchanged updated_at time will become earlier relative to the updated generated_timestamp time.
    use_cache = True

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Adds the field 'comment_count'"""
        params = super().request_params(**kwargs)
        params["include"] = "comment_count"
        return params


class TicketComments(SourceZendeskSupportStream):
    """TicketComments stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_comments/
    ZenDesk doesn't provide API for loading of all comments by one direct endpoints.
    Thus at first we loads all updated tickets and after this tries to load all created/updated
    comments per every ticket"""

    # Tickets can be removed throughout synchronization. The ZendDesk API will return a response
    # with 404 code if a ticket is not exists. But it shouldn't break loading of other comments.
    raise_on_http_errors = False
    parent = Tickets

    response_list_name = "comments"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # need to save a slice ticket state
        # because the function get_updated_state doesn't have a stream_slice as argument
        self._ticket_last_end_time = None

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ticket_id = stream_slice["id"]
        return f"tickets/{ticket_id}/comments.json"

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        tickets_stream = self.parent(start_date=self._start_date, subdomain=self._subdomain, authenticator=self._session.auth)
        for ticket in tickets_stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state):
            if ticket["comment_count"]:
                yield {"id": ticket["id"], "child_count": ticket["comment_count"]}


class Groups(SourceZendeskSupportStream):
    """Groups stream: https://developer.zendesk.com/api-reference/ticketing/groups/groups/"""


# TODO: fix to support future sync
# class GroupMemberships(SourceZendeskSupportStream):
#     """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""


class SatisfactionRatings(SourceZendeskSupportStream):
    """SatisfactionRatings stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/satisfaction_ratings/

    The ZenDesk API for this stream provides the filter "start_time" that can be used for incremental logic
    """

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        """Adds the filtering field 'start_time'"""
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        start_time = self.str2unixtime((stream_state or {}).get(self.cursor_field))

        if not start_time:
            start_time = self.str2unixtime(self._start_date)
        params.update(
            {
                "start_time": start_time,
                "sort_by": "asc",
            }
        )
        return params


# TODO: fix to support future sync (offset pagination is not supported)
# class TicketFields(SourceZendeskSupportStream):
#     """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


# class TicketForms(SourceZendeskSupportStream):
#     """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms/"""


class TicketMetrics(SourceZendeskSupportStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Tickets are ordered chronologically by created date, from newest to oldest.
        # No need to get next page once cursor passed initial state
        if self.is_finished:
            return None

        return super().next_page_token(response)


# TODO: fix to support future sync (offset pagination is not supported)
# class TicketMetricEvents(SourceZendeskSupportStream):
#     """TicketMetricEvents stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/"""
#
#     cursor_field = "time"


class Macros(SourceZendeskSupportStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


# endpoints provide a cursor pagination and sorting mechanism


# TODO: fix to support future sync (offset pagination is not supported)
# class TicketAudits(SourceZendeskSupportStream):
#     """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""
#
#     # can request a maximum of 1,000 results
#     page_size = 1000
#     # ticket audits doesn't have the 'updated_by' field
#     cursor_field = "created_at"
#
#     # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
#     response_list_name = "audits"
#
#     # This endpoint uses a variant of cursor pagination with some differences from cursor pagination used in other endpoints.
#     def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
#         params = super().request_params(next_page_token=next_page_token, **kwargs)
#         params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size})
#
#         if next_page_token:
#             params["cursor"] = next_page_token
#         return params
#
#     def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
#         if self.is_finished:
#             return None
#         return response.json().get("before_cursor")


# endpoints don't provide the updated_at/created_at fields
# thus we can't implement an incremental logic for them


class Tags(SourceZendeskSupportStream):
    """Tags stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/"""

    # doesn't have the 'id' field
    primary_key = "name"


# TODO: fix to support future sync (offset pagination is not supported, but has count in initial record)
class SlaPolicies(SourceZendeskSupportStream):
    """SlaPolicies stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"


class Brands(SourceZendeskSupportStream):
    """Brands stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands"""


class CustomRoles(SourceZendeskSupportStream):
    """CustomRoles stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles"""


class Schedules(SourceZendeskSupportStream):
    """Schedules stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules"""

    def path(self, *args, **kwargs) -> str:
        return "business_hours/schedules.json"
