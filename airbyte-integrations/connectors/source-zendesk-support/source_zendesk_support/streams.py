#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import calendar
import time
from abc import ABC
from collections import deque
from concurrent.futures import Future, ProcessPoolExecutor
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
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from requests_futures.sessions import PICKLE_ERROR, FuturesSession

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LAST_END_TIME_KEY = "_last_end_time"


class SourceZendeskException(Exception):
    """default exception of custom SourceZendesk logic"""


class SourceZendeskSupportFuturesSession(FuturesSession):
    """
    Check the docs at https://github.com/ross/requests-futures.
    Used to async execute a set of requests.
    """

    def send_future(self, request: requests.PreparedRequest, **kwargs) -> Future:
        """
        Use instead of default `Session.send()` method.
        `Session.send()` should not be overridden as it used by `requests-futures` lib.
        """

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


class BaseSourceZendeskSupportStream(HttpStream, ABC):
    def __init__(self, subdomain: str, start_date: str, **kwargs):
        super().__init__(**kwargs)

        self._start_date = start_date
        self._subdomain = subdomain

    def backoff_time(self, response: requests.Response) -> Union[int, float]:
        """
        The rate limit is 700 requests per minute
        # monitoring-your-request-activity
        See https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/
        The response has a Retry-After header that tells you for how many seconds to wait before retrying.
        """

        retry_after = int(response.headers.get("Retry-After", 0))
        if retry_after > 0:
            return retry_after

        # the header X-Rate-Limit returns the amount of requests per minute
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

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """try to select relevant data only"""

        records = response.json().get(self.response_list_name or self.name) or []
        if not self.cursor_field:
            yield from records
        else:
            cursor_date = (stream_state or {}).get(self.cursor_field)
            for record in records:
                updated = record[self.cursor_field]
                if not cursor_date or updated > cursor_date:
                    yield record


class SourceZendeskSupportStream(BaseSourceZendeskSupportStream):
    """Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    cursor_field = "updated_at"

    response_list_name: str = None
    parent: "SourceZendeskSupportStream" = None
    future_requests: deque = None

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, authenticator: Union[AuthBase, HttpAuthenticator] = None, **kwargs):
        super().__init__(**kwargs)

        self._session = SourceZendeskSupportFuturesSession()
        self._session.auth = authenticator
        self.future_requests = deque()

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def get_api_records_count(self, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None):
        """
        Count stream records before generating the future requests
        to then correctly generate the pagination parameters.
        """

        count_url = urljoin(self.url_base, f"{self.path(stream_state=stream_state, stream_slice=stream_slice)}/count.json")

        start_date = self._start_date
        params = {}
        if self.cursor_field and stream_state:
            start_date = stream_state.get(self.cursor_field)
        if start_date:
            params["start_time"] = self.str2datetime(start_date)

        response = self._session.request("get", count_url).result()
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
        for page_number in range(1, page_count + 1):
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice)
            params["page"] = page_number
            request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice)

            request = self._create_prepared_request(
                path=self.path(stream_state=stream_state, stream_slice=stream_slice),
                headers=dict(request_headers, **self.authenticator.get_auth_header()),
                params=params,
                json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice),
                data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice),
            )

            request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice)
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

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {}
        stream_state = stream_state or {}
        # try to search all records with generated_timestamp > start_time
        current_state = stream_state.get(self.cursor_field)
        if current_state and isinstance(current_state, str) and not current_state.isdigit():
            current_state = self.str2unixtime(current_state)
        start_time = current_state or calendar.timegm(pendulum.parse(self._start_date).utctimetuple())
        # +1 because the API returns all records where generated_timestamp >= start_time

        now = calendar.timegm(datetime.now().utctimetuple())
        if start_time > now - 60:
            # start_time must be more than 60 seconds ago
            start_time = now - 61
        params["start_time"] = start_time

        return params

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

            response = item["future"].result()

            if self.should_retry(response):
                backoff_time = self.backoff_time(response)
                if item["retries"] == self.max_retries:
                    raise DefaultBackoffException(request=item["request"], response=response)
                else:
                    if response.elapsed.total_seconds() < backoff_time:
                        time.sleep(backoff_time - response.elapsed.total_seconds())

                    self.future_requests.append(
                        {
                            "future": self._send_request(item["request"], item["request_kwargs"]),
                            "request": item["request"],
                            "request_kwargs": item["request_kwargs"],
                            "retries": item["retries"] + 1,
                            "backoff_time": backoff_time,
                        }
                    )
            else:
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

    def path(self, **kwargs):
        return self.name

    def next_page_token(self, *args, **kwargs):
        return None


class SourceZendeskSupportFullRefreshStream(BaseSourceZendeskSupportStream):
    primary_key = "id"
    response_list_name: str = None

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    def path(self, **kwargs):
        return self.name

    @staticmethod
    def _parse_next_page_number(response: requests.Response) -> Optional[int]:
        """Parses a response and tries to find next page number"""
        next_page = response.json().get("next_page")
        if next_page:
            return dict(parse_qsl(urlparse(next_page).query)).get("page")
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = self._parse_next_page_number(response)
        if not next_page:
            self._finished = True
            return None
        return next_page

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params.update(
            {
                "page": next_page_token or 1,
                "per_page": self.page_size,
            }
        )
        return params


class SourceZendeskSupportCursorPaginationStream(SourceZendeskSupportFullRefreshStream):
    next_page_field = "next_page"
    prev_start_time = None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        old_value = str((current_stream_state or {}).get(self.cursor_field, ""))
        new_value = str((latest_record or {}).get(self.cursor_field, ""))
        return {self.cursor_field: max(new_value, old_value)}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        start_time = dict(parse_qsl(urlparse(response.json().get(self.next_page_field), "").query)).get("start_time")
        if start_time != self.prev_start_time:
            self.prev_start_time = start_time
            return {self.cursor_field: start_time}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        if self.cursor_field:
            params = {
                "start_time": next_page_token.get(self.cursor_field, calendar.timegm(pendulum.parse(self._start_date).utctimetuple()))
            }
        else:
            params = {"start_time": calendar.timegm(pendulum.parse(self._start_date).utctimetuple())}
        return params


class Users(SourceZendeskSupportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Organizations(SourceZendeskSupportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Tickets(SourceZendeskSupportStream):
    """Tickets stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""

    # The API compares the start_time with the ticket's generated_timestamp value, not its updated_at value.
    # The generated_timestamp value is updated for all entity updates, including system updates.
    # If a system update occurs after an event, the unchanged updated_at time will become earlier
    # relative to the updated generated_timestamp time.

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
    # raise_on_http_errors = False

    parent = Tickets
    cursor_field = "created_at"

    response_list_name = "comments"

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ticket_id = stream_slice["id"]
        return f"tickets/{ticket_id}/comments"

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        tickets_stream = self.parent(start_date=self._start_date, subdomain=self._subdomain, authenticator=self._session.auth)
        for ticket in tickets_stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state):
            if ticket["comment_count"]:
                yield {"id": ticket["id"], "child_count": ticket["comment_count"]}


class Groups(SourceZendeskSupportStream):
    """Groups stream: https://developer.zendesk.com/api-reference/ticketing/groups/groups/"""


class GroupMemberships(SourceZendeskSupportCursorPaginationStream):
    """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""

    cursor_field = "updated_at"


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


class TicketFields(SourceZendeskSupportStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(SourceZendeskSupportCursorPaginationStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms/"""


class TicketMetrics(SourceZendeskSupportStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""


class TicketMetricEvents(SourceZendeskSupportCursorPaginationStream):
    """TicketMetricEvents stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/"""

    cursor_field = "time"

    def path(self, **kwargs):
        return "incremental/ticket_metric_events"


class Macros(SourceZendeskSupportStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


# endpoints provide a cursor pagination and sorting mechanism


class TicketAudits(SourceZendeskSupportCursorPaginationStream):
    """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""

    parent = Tickets
    # can request a maximum of 1,000 results
    page_size = 1000
    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"

    # This endpoint uses a variant of cursor pagination with some differences from cursor pagination used in other endpoints.
    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size}

        if next_page_token:
            params["cursor"] = next_page_token
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return response.json().get("before_cursor")


# endpoints don't provide the updated_at/created_at fields
# thus we can't implement an incremental logic for them


class Tags(SourceZendeskSupportFullRefreshStream):
    """Tags stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/"""

    # doesn't have the 'id' field
    primary_key = "name"


class SlaPolicies(SourceZendeskSupportFullRefreshStream):
    """SlaPolicies stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"


class Brands(SourceZendeskSupportFullRefreshStream):
    """Brands stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands"""


class CustomRoles(SourceZendeskSupportFullRefreshStream):
    """CustomRoles stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles"""


class Schedules(SourceZendeskSupportFullRefreshStream):
    """Schedules stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules"""

    def path(self, *args, **kwargs) -> str:
        return "business_hours/schedules.json"


class UserSettingsStream(SourceZendeskSupportFullRefreshStream):
    """Stream for checking of a request token and permissions"""

    def path(self, *args, **kwargs) -> str:
        return "account/settings.json"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""
        settings = response.json().get("settings")
        if settings:
            yield settings

    def get_settings(self) -> Mapping[str, Any]:
        for resp in self.read_records(SyncMode.full_refresh):
            return resp
        raise SourceZendeskException("not found settings")
