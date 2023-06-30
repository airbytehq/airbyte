#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import calendar
import functools
import logging
import re
import time
from abc import ABC
from collections import deque
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import datetime, timedelta
from functools import partial
from math import ceil
from pickle import PickleError, dumps
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urljoin, urlparse

import pendulum
import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.rate_limiting import TRANSIENT_EXCEPTIONS
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from requests_futures.sessions import PICKLE_ERROR, FuturesSession
from source_zendesk_support.ZendeskSupportAvailabilityStrategy import ZendeskSupportAvailabilityStrategy

DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
LAST_END_TIME_KEY: str = "_last_end_time"
END_OF_STREAM_KEY: str = "end_of_stream"

logger = logging.getLogger("airbyte")

# For some streams, multiple http requests are running at the same time for performance reasons.
# However, it may result in hitting the rate limit, therefore subsequent requests have to be made after a pause.
# The idea is to sustain a pause once and continue making multiple requests at a time.
# A single `retry_at` variable is introduced here, which prevents us from duplicate sleeping in the main thread
# before each request is made as it used to be in prior versions.
# It acts like a global counter - increased each time a 429 status is met
# only if it is greater than the current value. On the other hand, no request may be made before this moment.
# Because the requests are made in parallel, time.sleep will be called in parallel as well.
# This is possible because it is a point in time, not timedelta.
retry_at: Optional[datetime] = None


def sleep_before_executing(sleep_time: float):
    def wrapper(function):
        @functools.wraps(function)
        def inner(*args, **kwargs):
            logger.info(f"Sleeping {sleep_time} seconds before next request")
            time.sleep(int(sleep_time))
            result = function(*args, **kwargs)
            return result, datetime.utcnow()

        return inner

    return wrapper


def to_int(s):
    "https://github.com/airbytehq/airbyte/issues/13673"
    if isinstance(s, str):
        res = re.findall(r"[-+]?\d+", s)
        if res:
            return res[0]
    return s


class SourceZendeskException(Exception):
    """default exception of custom SourceZendesk logic"""


class SourceZendeskSupportFuturesSession(FuturesSession):
    """
    Check the docs at https://github.com/ross/requests-futures
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
            sleep_time = 0
            now = datetime.utcnow()
            if retry_at and retry_at > now:
                sleep_time = (retry_at - datetime.utcnow()).seconds
            # avoid calling super to not break pickled method
            func = partial(requests.Session.send, self)
            func = sleep_before_executing(sleep_time)(func)

        if isinstance(self.executor, ProcessPoolExecutor):
            self.logger.warning("ProcessPoolExecutor is used to perform IO related tasks for unknown reason!")
            # verify function can be pickled
            try:
                dumps(func)
            except (TypeError, PickleError):
                raise RuntimeError(PICKLE_ERROR)

        return self.executor.submit(func, request, **kwargs)


class BaseSourceZendeskSupportStream(HttpStream, ABC):
    raise_on_http_errors = True

    def __init__(self, subdomain: str, start_date: str, ignore_pagination: bool = False, **kwargs):
        super().__init__(**kwargs)

        self._start_date = start_date
        self._subdomain = subdomain
        self._ignore_pagination = ignore_pagination

    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return HttpAvailabilityStrategy()

    def backoff_time(self, response: requests.Response) -> Union[int, float]:
        """
        The rate limit is 700 requests per minute
        # monitoring-your-request-activity
        See https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/
        The response has a Retry-After header that tells you for how many seconds to wait before retrying.
        """

        retry_after = int(to_int(response.headers.get("Retry-After", 0)))
        if retry_after > 0:
            return retry_after

        # the header X-Rate-Limit returns the amount of requests per minute
        rate_limit = float(response.headers.get("X-Rate-Limit", 0))
        if rate_limit and rate_limit > 0:
            return 60.0 / rate_limit
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

    @staticmethod
    def _parse_next_page_number(response: requests.Response) -> Optional[int]:
        """Parses a response and tries to find next page number"""
        try:
            next_page = response.json().get("next_page")
        except requests.exceptions.JSONDecodeError:
            next_page = None

        return dict(parse_qsl(urlparse(next_page).query)).get("page") if next_page else None

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """try to select relevant data only"""

        try:
            records = response.json().get(self.response_list_name or self.name) or []
        except requests.exceptions.JSONDecodeError:
            records = []

        if not self.cursor_field:
            yield from records
        else:
            cursor_date = (stream_state or {}).get(self.cursor_field)
            for record in records:
                updated = record[self.cursor_field]
                if not cursor_date or updated > cursor_date:
                    yield record

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 403:
            try:
                error = response.json().get("error")
            except requests.exceptions.JSONDecodeError:
                error = {"title": "Forbidden", "message": "Received empty JSON response"}
            self.logger.error(f"Skipping stream {self.name}: Check permissions, error message: {error}.")
            setattr(self, "raise_on_http_errors", False)
            return False
        return super().should_retry(response)


class SourceZendeskSupportStream(BaseSourceZendeskSupportStream):
    """Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    cursor_field = "updated_at"

    response_list_name: str = None
    future_requests: deque = None

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, authenticator: Union[AuthBase, HttpAuthenticator] = None, **kwargs):
        super().__init__(**kwargs)

        self._session = SourceZendeskSupportFuturesSession()
        self._session.auth = authenticator
        self.future_requests = deque()

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return ZendeskSupportAvailabilityStrategy()

    def path(self, **kwargs):
        return self.name

    def next_page_token(self, *args, **kwargs):
        return None

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
        self.logger.info(f"Records count is {records_count}")
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
                }
            )
        self.logger.info(f"Generated {len(self.future_requests)} future requests")

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> Future:
        response: Future = self._session.send_future(request, **request_kwargs)
        return response

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> Future:
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

    def _retry(
        self,
        request: requests.PreparedRequest,
        retries: int,
        original_exception: Exception = None,
        response: requests.Response = None,
        finished_at: Optional[datetime] = None,
        **request_kwargs,
    ):
        if retries == self.max_retries:
            if original_exception:
                raise original_exception
            raise DefaultBackoffException(request=request, response=response)
        if response is not None:
            sleep_time = self.backoff_time(response)
            if finished_at and sleep_time:
                current_retry_at = finished_at + timedelta(seconds=sleep_time)
                global retry_at
                if not retry_at or (retry_at < current_retry_at):
                    retry_at = current_retry_at
                self.logger.info(f"Adding a request to be retried in {sleep_time} seconds")
        self.future_requests.append(
            {
                "future": self._send_request(request, request_kwargs),
                "request": request,
                "request_kwargs": request_kwargs,
                "retries": retries + 1,
            }
        )

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.generate_future_requests(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)

        while len(self.future_requests) > 0:
            self.logger.info("Starting another while loop iteration")
            item = self.future_requests.popleft()
            request, retries, future, kwargs = item["request"], item["retries"], item["future"], item["request_kwargs"]

            try:
                response, finished_at = future.result()
            except TRANSIENT_EXCEPTIONS as exc:
                self.logger.info("Will retry the request because of a transient exception")
                self._retry(request=request, retries=retries, original_exception=exc, **kwargs)
                continue
            if self.should_retry(response):
                self.logger.info("Will retry the request for other reason")
                self._retry(request=request, retries=retries, response=response, finished_at=finished_at, **kwargs)
                continue
            self.logger.info("Request successful, will parse the response now")
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)


class SourceZendeskSupportFullRefreshStream(BaseSourceZendeskSupportStream):
    """
    Endpoints don't provide the updated_at/created_at fields
    Thus we can't implement an incremental logic for them
    """

    page_size = 100
    primary_key = "id"
    response_list_name: str = None

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    def path(self, **kwargs):
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
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
    """
    Endpoints provide a cursor pagination and sorting mechanism
    """

    cursor_field = "updated_at"
    next_page_field = "next_page"
    prev_start_time = None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        old_value = str((current_stream_state or {}).get(self.cursor_field, ""))
        new_value = str((latest_record or {}).get(self.cursor_field, ""))
        return {self.cursor_field: max(new_value, old_value)}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        start_time = dict(parse_qsl(urlparse(response.json().get(self.next_page_field), "").query)).get("start_time")
        if start_time != self.prev_start_time:
            self.prev_start_time = start_time
            return {self.cursor_field: int(start_time)}

    def check_stream_state(self, stream_state: Mapping[str, Any] = None):
        """
        Returns the state value, if exists. Otherwise, returns user defined `Start Date`.
        """
        state = stream_state.get(self.cursor_field) or self._start_date if stream_state else self._start_date
        return calendar.timegm(pendulum.parse(state).utctimetuple())

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        if self.cursor_field:
            params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        else:
            params = {"start_time": calendar.timegm(pendulum.parse(self._start_date).utctimetuple())}
        return params


class SourceZendeskIncrementalExportStream(SourceZendeskSupportCursorPaginationStream):
    """Incremental Export from Tickets stream:
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based

    @ param response_list_name: the main nested entity to look at inside of response, default = response_list_name
    @ param sideload_param : parameter variable to include various information to response
        more info: https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/side_loading/#supported-endpoints
    """

    response_list_name: str = None
    sideload_param: str = None

    @staticmethod
    def check_start_time_param(requested_start_time: int, value: int = 1):
        """
        Requesting tickets in the future is not allowed, hits 400 - bad request.
        We get current UNIX timestamp minus `value` from now(), default = 1 (minute).

        Returns: either close to now UNIX timestamp or previously requested UNIX timestamp.
        """
        now = calendar.timegm(pendulum.now().subtract(minutes=value).utctimetuple())
        return now if requested_start_time > now else requested_start_time

    def path(self, **kwargs) -> str:
        return f"incremental/{self.response_list_name}.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Returns next_page_token based on `end_of_stream` parameter inside of response
        """
        next_page_token = super().next_page_token(response)
        return None if response.json().get(END_OF_STREAM_KEY, False) else next_page_token

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in response.json().get(self.response_list_name, []):
            yield record


class SourceZendeskSupportTicketEventsExportStream(SourceZendeskIncrementalExportStream):
    """Incremental Export from TicketEvents stream:
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export

    @ param response_list_name: the main nested entity to look at inside of response, default = "ticket_events"
    @ param response_target_entity: nested property inside of `response_list_name`, default = "child_events"
    @ param list_entities_from_event : the list of nested child_events entities to include from parent record
    @ param event_type : specific event_type to check ["Audit", "Change", "Comment", etc]
    """

    cursor_field = "created_at"
    response_list_name: str = "ticket_events"
    response_target_entity: str = "child_events"
    list_entities_from_event: List[str] = None
    event_type: str = None

    @property
    def update_event_from_record(self) -> bool:
        """Returns True/False based on list_entities_from_event property"""
        return True if len(self.list_entities_from_event) > 0 else False

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            for event in record.get(self.response_target_entity, []):
                if event.get("event_type") == self.event_type:
                    if self.update_event_from_record:
                        for prop in self.list_entities_from_event:
                            event[prop] = record.get(prop)
                    yield event


class OrganizationMemberships(SourceZendeskSupportCursorPaginationStream):
    """OrganizationMemberships stream: https://developer.zendesk.com/api-reference/ticketing/organizations/organization_memberships/"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        meta = response.json().get("meta", {})
        return meta.get("after_cursor") if meta.get("has_more", False) else None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {
            "start_time": self.check_stream_state(stream_state),
            "page[size]": self.page_size,
        }
        if next_page_token:
            params.pop("start_time", None)
            params["page[after]"] = next_page_token
        return params


class AuditLogs(SourceZendeskSupportCursorPaginationStream):
    """AuditLogs stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs"""

    # can request a maximum of 1,00 results
    page_size = 100
    # audit_logs doesn't have the 'updated_by' field
    cursor_field = "created_at"


class Users(SourceZendeskIncrementalExportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export"""

    response_list_name: str = "users"


class Organizations(SourceZendeskSupportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Posts(SourceZendeskSupportCursorPaginationStream):
    """Posts stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/posts/#list-posts"""

    cursor_field = "updated_at"

    def path(self, **kwargs):
        return "community/posts"


class Tickets(SourceZendeskIncrementalExportStream):
    """Tickets stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based"""

    response_list_name: str = "tickets"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @staticmethod
    def check_start_time_param(requested_start_time: int, value: int = 1):
        """
        The stream returns 400 Bad Request StartTimeTooRecent when requesting tasks 1 second before now.
        Figured out during experiments that the most recent time needed for request to be successful is 3 seconds before now.
        """
        return SourceZendeskIncrementalExportStream.check_start_time_param(requested_start_time, value=3)


class TicketComments(SourceZendeskSupportTicketEventsExportStream):
    """
    Fetch the TicketComments incrementaly from TicketEvents Export stream
    """

    list_entities_from_event = ["via_reference_id", "ticket_id", "timestamp"]
    sideload_param = "comment_events"
    event_type = "Comment"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            # https://github.com/airbytehq/oncall/issues/1001
            if type(record.get("via")) is not dict:
                record["via"] = None
            yield record


class Groups(SourceZendeskSupportStream):
    """Groups stream: https://developer.zendesk.com/api-reference/ticketing/groups/groups/"""


class GroupMemberships(SourceZendeskSupportCursorPaginationStream):
    """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        next_page = self._parse_next_page_number(response)
        return next_page if next_page else None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"page": 1, "per_page": self.page_size, "sort_by": "asc"}
        start_time = self.str2unixtime((stream_state or {}).get(self.cursor_field))
        params["start_time"] = start_time if start_time else self.str2unixtime(self._start_date)
        if next_page_token:
            params["page"] = next_page_token
        return params


class SatisfactionRatings(SourceZendeskSupportCursorPaginationStream):
    """
    SatisfactionRatings stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/satisfaction_ratings/
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        next_page = self._parse_next_page_number(response)
        return next_page if next_page else None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"page": 1, "per_page": self.page_size, "sort_by": "asc"}
        start_time = self.str2unixtime((stream_state or {}).get(self.cursor_field))
        params["start_time"] = start_time if start_time else self.str2unixtime(self._start_date)
        if next_page_token:
            params["page"] = next_page_token
        return params


class TicketFields(SourceZendeskSupportStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(SourceZendeskSupportCursorPaginationStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms"""


class TicketMetrics(SourceZendeskSupportCursorPaginationStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        https://developer.zendesk.com/documentation/api-basics/pagination/paginating-through-lists-using-cursor-pagination/#when-to-stop-paginating
        """
        meta = response.json().get("meta", {})
        return meta.get("after_cursor") if meta.get("has_more", False) else None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        """
        To make the Cursor Pagination to return `after_cursor` we should follow these instructions:
        https://developer.zendesk.com/documentation/api-basics/pagination/paginating-through-lists-using-cursor-pagination/#enabling-cursor-pagination
        """
        params = {
            "start_time": self.check_stream_state(stream_state),
            "page[size]": self.page_size,
        }
        if next_page_token:
            # when cursor pagination is used, we can pass only `after` and `page size` params,
            # other params should be omitted.
            params.pop("start_time", None)
            params["page[after]"] = next_page_token
        return params


class TicketSkips(SourceZendeskSupportCursorPaginationStream):
    """TicketSkips stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/"""

    response_list_name = "skips"

    def path(self, **kwargs):
        return "skips.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        meta = response.json().get("meta", {})
        return meta.get("after_cursor") if meta.get("has_more", False) else None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {
            "start_time": self.check_stream_state(stream_state),
            "page[size]": self.page_size,
        }
        if next_page_token:
            params.pop("start_time", None)
            params["page[after]"] = next_page_token
        return params


class TicketMetricEvents(SourceZendeskSupportCursorPaginationStream):
    """
    TicketMetricEvents stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/
    """

    cursor_field = "time"

    def path(self, **kwargs):
        return "incremental/ticket_metric_events"


class Macros(SourceZendeskSupportStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


class TicketAudits(SourceZendeskSupportCursorPaginationStream):
    """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""

    # can request a maximum of 1,000 results
    page_size = 1000
    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    # This endpoint uses a variant of cursor pagination with some differences from cursor pagination used in other endpoints.
    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size}

        if next_page_token:
            params["cursor"] = next_page_token
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        return response.json().get("before_cursor")


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


class AccountAttributes(SourceZendeskSupportFullRefreshStream):
    """Account attributes stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-account-attributes"""

    response_list_name = "attributes"

    def path(self, *args, **kwargs) -> str:
        return "routing/attributes"


class AttributeDefinitions(SourceZendeskSupportFullRefreshStream):
    """Attribute definitions stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-routing-attribute-definitions"""

    primary_key = None

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        for definition in response.json()["definitions"]["conditions_all"]:
            definition["condition"] = "all"
            yield definition
        for definition in response.json()["definitions"]["conditions_any"]:
            definition["confition"] = "any"
            yield definition

    def path(self, *args, **kwargs) -> str:
        return "routing/attributes/definitions"


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
