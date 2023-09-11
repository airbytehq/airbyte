#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import calendar
import logging
import re
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import StreamData, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType

DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
LAST_END_TIME_KEY: str = "_last_end_time"
END_OF_STREAM_KEY: str = "end_of_stream"

logger = logging.getLogger("airbyte")


def to_int(s):
    """https://github.com/airbytehq/airbyte/issues/13673"""
    if isinstance(s, str):
        res = re.findall(r"[-+]?\d+", s)
        if res:
            return res[0]
    return s


class ZendeskConfigException(AirbyteTracedException):
    """default config exception to custom SourceZendesk logic"""

    def __init__(self, **kwargs):
        failure_type: FailureType = FailureType.config_error
        super(ZendeskConfigException, self).__init__(failure_type=failure_type, **kwargs)


class BaseZendeskSupportStream(HttpStream, ABC):
    raise_on_http_errors = True

    def __init__(self, subdomain: str, start_date: str, ignore_pagination: bool = False, **kwargs):
        super().__init__(**kwargs)

        self._start_date = start_date
        self._subdomain = subdomain
        self._ignore_pagination = ignore_pagination

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
        status_code = response.status_code
        if status_code == 403 or status_code == 404:
            try:
                error = response.json().get("error")
            except requests.exceptions.JSONDecodeError:
                reason = response.reason
                error = {"title": f"{reason}", "message": "Received empty JSON response"}
            self.logger.error(
                f"Skipping stream {self.name}, error message: {error}. Please ensure the authenticated user has access to this stream. If the issue persists, contact Zendesk support."
            )
            setattr(self, "raise_on_http_errors", False)
            return False
        return super().should_retry(response)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        try:
            yield from super().read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
        except requests.exceptions.JSONDecodeError:
            self.logger.error(
                f"Skipping stream {self.name}: Non-JSON response received. Please ensure that you have enough permissions for this stream."
            )


class SourceZendeskSupportStream(BaseZendeskSupportStream):
    """Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    cursor_field = "updated_at"

    response_list_name: str = None

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    def path(self, **kwargs):
        return self.name

    def next_page_token(self, *args, **kwargs):
        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
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


class FullRefreshZendeskSupportStream(BaseZendeskSupportStream):
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

        meta = response.json().get("meta", {}) if response.content else {}
        return {"page[after]": meta.get("after_cursor")} if meta.get("has_more") else None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"page[size]": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalZendeskSupportStream(FullRefreshZendeskSupportStream):
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

    def check_stream_state(self, stream_state: Mapping[str, Any] = None) -> int:
        """
        Returns the state value, if exists. Otherwise, returns user defined `Start Date`.
        """
        state = stream_state.get(self.cursor_field) or self._start_date if stream_state else self._start_date
        return calendar.timegm(pendulum.parse(state).utctimetuple())


class CursorPaginationZendeskSupportStream(IncrementalZendeskSupportStream):
    """Zendesk Support Cursor Pagination, see https://developer.zendesk.com/api-reference/introduction/pagination/#using-cursor-pagination"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None

        meta = response.json().get("meta", {})
        return {"page[after]": meta.get("after_cursor")} if meta.get("has_more") else None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "start_time": self.check_stream_state(stream_state),
            "page[size]": self.page_size,
        }
        if next_page_token:
            params.pop("start_time", None)
            params.update(next_page_token)
        return params


class TimeBasedPaginationZendeskSupportStream(IncrementalZendeskSupportStream):
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        start_time = dict(parse_qsl(urlparse(response.json().get(self.next_page_field), "").query)).get("start_time")
        if start_time != self.prev_start_time:
            self.prev_start_time = start_time
            return {self.cursor_field: int(start_time)}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        if self.cursor_field:
            params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        else:
            params = {"start_time": calendar.timegm(pendulum.parse(self._start_date).utctimetuple())}
        return params


class SourceZendeskIncrementalExportStream(IncrementalZendeskSupportStream):
    """Incremental Export from Tickets stream:
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based

    @ param response_list_name: the main nested entity to look at inside of response, default = response_list_name
    @ param sideload_param : parameter variable to include various information to response
        more info: https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/side_loading/#supported-endpoints
    """

    response_list_name: str = None
    sideload_param: str = None

    @staticmethod
    def check_start_time_param(requested_start_time: int, value: int = 1) -> int:
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
        if self._ignore_pagination:
            return None
        response_json = response.json()
        return None if response_json.get(END_OF_STREAM_KEY, True) else {"cursor": response_json.get("after_cursor")}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.pop("start_time", None)
            params.update(next_page_token)
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

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"incremental/{self.response_list_name}.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Returns next_page_token based on `end_of_stream` parameter inside of response
        """
        response_json = response.json()
        return None if response_json.get(END_OF_STREAM_KEY, True) else {"start_time": response_json.get("end_time")}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.update(next_page_token)
        return params

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


class OrganizationMemberships(CursorPaginationZendeskSupportStream):
    """OrganizationMemberships stream: https://developer.zendesk.com/api-reference/ticketing/organizations/organization_memberships/"""


class OrganizationFields(CursorPaginationZendeskSupportStream):
    """OrganizationMemberships stream: https://developer.zendesk.com/api-reference/ticketing/organizations/organization_fields/#list-organization-fields"""


class AuditLogs(CursorPaginationZendeskSupportStream):
    """AuditLogs stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/audit_logs/#list-audit-logs"""

    # can request a maximum of 100 results
    page_size = 100
    # audit_logs doesn't have the 'updated_by' field
    cursor_field = "created_at"


class Users(SourceZendeskIncrementalExportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export"""

    response_list_name: str = "users"

    def path(self, **kwargs) -> str:
        return "incremental/users/cursor.json"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.update(next_page_token)
        return params


class Organizations(SourceZendeskIncrementalExportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""

    response_list_name: str = "organizations"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.update(next_page_token)
        return params


class Posts(CursorPaginationZendeskSupportStream):
    """Posts stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/posts/#list-posts"""

    use_cache = True

    cursor_field = "updated_at"

    def path(self, **kwargs):
        return "community/posts"


class Tickets(SourceZendeskIncrementalExportStream):
    """Tickets stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based"""

    response_list_name: str = "tickets"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    cursor_field = "generated_timestamp"

    def path(self, **kwargs) -> str:
        return "incremental/tickets/cursor.json"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        parsed_state = self.check_stream_state(stream_state)
        params = {"start_time": self.check_start_time_param(parsed_state)}
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.update(next_page_token)
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        old_value = (current_stream_state or {}).get(self.cursor_field, pendulum.parse(self._start_date).int_timestamp)
        new_value = (latest_record or {}).get(self.cursor_field, pendulum.parse(self._start_date).int_timestamp)
        return {self.cursor_field: max(new_value, old_value)}

    def check_stream_state(self, stream_state: Mapping[str, Any] = None) -> int:
        """
        Returns the state value, if exists. Otherwise, returns user defined `Start Date`.
        """
        return stream_state.get(self.cursor_field) if stream_state else pendulum.parse(self._start_date).int_timestamp

    def check_start_time_param(self, requested_start_time: int, value: int = 1) -> int:
        """
        The stream returns 400 Bad Request StartTimeTooRecent when requesting tasks 1 second before now.
        Figured out during experiments that the most recent time needed for request to be successful is 3 seconds before now.
        """
        return super().check_start_time_param(requested_start_time, value=3)


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


class GroupMemberships(CursorPaginationZendeskSupportStream):
    """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"sort_by": "asc"})
        return params


class SatisfactionRatings(CursorPaginationZendeskSupportStream):
    """
    SatisfactionRatings stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/satisfaction_ratings/
    """

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"sort_by": "asc"})
        return params


class TicketFields(SourceZendeskSupportStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(TimeBasedPaginationZendeskSupportStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms"""


class TicketMetrics(CursorPaginationZendeskSupportStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""


class TicketSkips(CursorPaginationZendeskSupportStream):
    """TicketSkips stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_skips/"""

    response_list_name = "skips"

    def path(self, **kwargs):
        return "skips.json"


class TicketMetricEvents(CursorPaginationZendeskSupportStream):
    """
    TicketMetricEvents stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metric_events/
    """

    cursor_field = "time"

    def path(self, **kwargs):
        return "incremental/ticket_metric_events"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "start_time": self.check_stream_state(stream_state),
            "page[size]": self.page_size,
        }
        if next_page_token:  # need keep start_time for this stream
            params.update(next_page_token)
        return params


class Macros(SourceZendeskSupportStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


class TicketAudits(IncrementalZendeskSupportStream):
    """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""

    # can request a maximum of 1,000 results
    page_size = 1000
    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    # This endpoint uses a variant of cursor pagination with some differences from cursor pagination used in other endpoints.
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size}
        if next_page_token:
            params.pop("start_time", None)
            params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None
        response_json = response.json()
        return {"cursor": response.json().get("before_cursor")} if response_json.get("before_cursor") else None


class Tags(FullRefreshZendeskSupportStream):
    """Tags stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/"""

    # doesn't have the 'id' field
    primary_key = "name"


class Topics(CursorPaginationZendeskSupportStream):
    """
    Topics stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/topics/#list-topics
    """

    cursor_field = "updated_at"

    def path(self, **kwargs):
        return "community/topics"


class SlaPolicies(IncrementalZendeskSupportStream):
    """SlaPolicies stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class Brands(FullRefreshZendeskSupportStream):
    """Brands stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/brands/#list-brands"""


class CustomRoles(IncrementalZendeskSupportStream):
    """CustomRoles stream: https://developer.zendesk.com/api-reference/ticketing/account-configuration/custom_roles/#list-custom-roles"""

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class Schedules(IncrementalZendeskSupportStream):
    """Schedules stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/schedules/#list-schedules"""

    def path(self, *args, **kwargs) -> str:
        return "business_hours/schedules.json"


class AccountAttributes(FullRefreshZendeskSupportStream):
    """Account attributes stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-account-attributes"""

    response_list_name = "attributes"

    def path(self, *args, **kwargs) -> str:
        return "routing/attributes"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class AttributeDefinitions(FullRefreshZendeskSupportStream):
    """Attribute definitions stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/skill_based_routing/#list-routing-attribute-definitions"""

    primary_key = None

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        for definition in response.json()["definitions"]["conditions_all"]:
            definition["condition"] = "all"
            yield definition
        for definition in response.json()["definitions"]["conditions_any"]:
            definition["condition"] = "any"
            yield definition

    def path(self, *args, **kwargs) -> str:
        return "routing/attributes/definitions"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class UserSettingsStream(FullRefreshZendeskSupportStream):
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
        raise ZendeskConfigException(message="Can not get access to settings endpoint; Please check provided credentials")

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class UserFields(FullRefreshZendeskSupportStream):
    """User Fields stream: https://developer.zendesk.com/api-reference/ticketing/users/user_fields/#list-user-fields"""

    def path(self, *args, **kwargs) -> str:
        return "user_fields"


class PostComments(CursorPaginationZendeskSupportStream, HttpSubStream):
    """Post Comments Stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/post_comments/"""

    response_list_name = "comments"

    def __init__(self, **kwargs):
        parent = Posts(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        post_id = stream_slice.get("parent").get("id")
        return f"community/posts/{post_id}/comments"


class AbstractVotes(CursorPaginationZendeskSupportStream, ABC):
    response_list_name = "votes"

    def get_json_schema(self) -> Mapping[str, Any]:
        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("votes")


class PostVotes(AbstractVotes, HttpSubStream):
    def __init__(self, **kwargs):
        parent = Posts(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        post_id = stream_slice.get("parent").get("id")
        return f"community/posts/{post_id}/votes"


class PostCommentVotes(AbstractVotes, HttpSubStream):
    def __init__(self, **kwargs):
        parent = PostComments(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        post_id = stream_slice.get("parent").get("post_id")
        comment_id = stream_slice.get("parent").get("id")
        return f"community/posts/{post_id}/comments/{comment_id}/votes"


class Articles(SourceZendeskIncrementalExportStream):
    """Articles Stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/articles/#list-articles"""

    response_list_name: str = "articles"

    def path(self, **kwargs) -> str:
        return "help_center/incremental/articles"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        next_page_token = next_page_token or {}
        parsed_state = self.check_stream_state(stream_state)
        params = {"sort_by": "updated_at", "sort_order": "asc", "start_time": next_page_token.get(self.cursor_field, parsed_state)}
        # check "start_time" is not in the future
        params["start_time"] = self.check_start_time_param(params["start_time"])
        if self.sideload_param:
            params["include"] = self.sideload_param
        if next_page_token:
            params.update(next_page_token)
        return params


class ArticleVotes(AbstractVotes, HttpSubStream):
    def __init__(self, **kwargs):
        parent = Articles(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        article_id = stream_slice.get("parent").get("id")
        return f"help_center/articles/{article_id}/votes"


class ArticleComments(CursorPaginationZendeskSupportStream, HttpSubStream):
    response_list_name = "comments"

    def __init__(self, **kwargs):
        parent = Articles(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        article_id = stream_slice.get("parent").get("id")
        return f"help_center/articles/{article_id}/comments"


class ArticleCommentVotes(AbstractVotes, HttpSubStream):
    def __init__(self, **kwargs):
        parent = ArticleComments(**kwargs)
        super().__init__(parent=parent, **kwargs)

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        article_id = stream_slice.get("parent").get("source_id")
        comment_id = stream_slice.get("parent").get("id")
        return f"help_center/articles/{article_id}/comments/{comment_id}/votes"


class DeletedTickets(CursorPaginationZendeskSupportStream):
    """Deleted Tickets Stream https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#list-deleted-tickets"""

    response_list_name: str = "deleted_tickets"
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    cursor_field = "deleted_at"

    def path(self, **kwargs) -> str:
        return "deleted_tickets.json"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "sort_by": self.cursor_field,
            "page[size]": self.page_size,
        }
        if next_page_token:
            params.update(next_page_token)
        return params
