#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import calendar
import copy
import logging
import re
from abc import ABC
from datetime import datetime
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import pytz
import requests

from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.streams.core import StreamData, package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException


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


class ZendeskSupportBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], attempt_count: int
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            retry_after = int(to_int(response_or_exception.headers.get("Retry-After", 0)))
            if retry_after > 0:
                return retry_after

            # the header X-Rate-Limit returns the amount of requests per minute
            rate_limit = float(response_or_exception.headers.get("X-Rate-Limit", 0))
            if rate_limit and rate_limit > 0:
                return 60.0 / rate_limit
        return None


class BaseZendeskSupportStream(HttpStream, ABC):
    def __init__(self, subdomain: str, start_date: str, ignore_pagination: bool = False, **kwargs):
        super().__init__(**kwargs)

        self._start_date = start_date
        self._subdomain = subdomain
        self._ignore_pagination = ignore_pagination

    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return ZendeskSupportBackoffStrategy()

    @staticmethod
    def str_to_datetime(str_dt: str) -> datetime:
        """convert string to datetime object
        Input example: '2021-07-22T06:55:55Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        if not str_dt:
            return None
        return datetime.strptime(str_dt, DATETIME_FORMAT)

    @staticmethod
    def datetime_to_str(dt: datetime) -> str:
        """convert datetime object to string
        Output example: '2021-07-22T06:55:55Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        return datetime.strftime(dt.replace(tzinfo=pytz.UTC), DATETIME_FORMAT)

    @staticmethod
    def str_to_unixtime(str_dt: str) -> Optional[int]:
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

    def get_error_handler(self) -> Optional[ErrorHandler]:
        error_mapping = DEFAULT_ERROR_MAPPING | {
            403: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Forbidden. Please ensure the authenticated user has access to this stream. If the issue persists, contact Zendesk support.",
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Not found. Please ensure the authenticated user has access to this stream. If the issue persists, contact Zendesk support.",
            ),
        }
        return HttpStatusErrorHandler(logger=self.logger, max_retries=10, error_mapping=error_mapping)

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
            current_state = self.str_to_unixtime(current_state)
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

    def get_stream_state_value(self, stream_state: Mapping[str, Any] = None) -> int:
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
            "start_time": self.get_stream_state_value(stream_state),
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
        parsed_state = self.get_stream_state_value(stream_state)
        if self.cursor_field:
            params = {"start_time": next_page_token.get(self.cursor_field, parsed_state)}
        else:
            params = {"start_time": calendar.timegm(pendulum.parse(self._start_date).utctimetuple())}
        return params


class SourceZendeskIncrementalExportStream(IncrementalZendeskSupportStream):
    """Incremental Export from Tickets stream:
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-export-time-based

    @ param response_list_name: the main nested entity to look at inside of response, default = response_list_name
        more info: https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/side_loading/#supported-endpoints
    """

    @property
    def response_list_name(self) -> str:
        raise NotImplementedError("The `response_list_name` must be implemented")

    @property
    def next_page_field(self) -> str:
        raise NotImplementedError("The `next_page_field` varies depending on stream and must be set individually")

    @staticmethod
    def validate_start_time(requested_start_time: int, value: int = 1) -> int:
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
        if END_OF_STREAM_KEY in response_json and response_json[END_OF_STREAM_KEY]:
            return None
        return dict(parse_qsl(urlparse(response_json.get(self.next_page_field, "")).query))

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Request params are based on parsed query params of next page url.
        `start_time` will be included as the initial request parameter and will never be changed unless it is itself a next page token.
        """
        if next_page_token:
            return next_page_token
        start_time = self.get_stream_state_value(stream_state)
        return {"start_time": self.validate_start_time(start_time)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in response.json().get(self.response_list_name, []):
            yield record


class SourceZendeskSupportTicketEventsExportStream(SourceZendeskIncrementalExportStream):
    """Incremental Export from TicketEvents stream:
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export

    @ param response_list_name: the main nested entity to look at inside of response, default = "ticket_events"
    @ param response_target_entity: nested property inside `response_list_name`, default = "child_events"
    @ param list_entities_from_event : the list of nested child_events entities to include from parent record
    @ param event_type : specific event_type to check ["Audit", "Change", "Comment", etc.]
    @ param sideload_param : parameter variable to include various information to response
    """

    cursor_field = "created_at"
    event_type: str = None
    list_entities_from_event: List[str] = None
    response_list_name: str = "ticket_events"
    response_target_entity: str = "child_events"
    sideload_param: str = None
    next_page_field: str = "next_page"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if self.sideload_param:
            params["include"] = self.sideload_param
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


class Automations(FullRefreshZendeskSupportStream):
    """Automations stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/automations/#list-automations"""


class Users(SourceZendeskIncrementalExportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export"""

    response_list_name: str = "users"
    next_page_field: str = "after_url"

    def path(self, **kwargs) -> str:
        return "incremental/users/cursor.json"


class Organizations(SourceZendeskIncrementalExportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""

    response_list_name: str = "organizations"
    next_page_field: str = "next_page"


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
    next_page_field = "after_url"

    def path(self, **kwargs) -> str:
        return "incremental/tickets/cursor.json"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        old_value = (current_stream_state or {}).get(self.cursor_field, pendulum.parse(self._start_date).int_timestamp)
        new_value = (latest_record or {}).get(self.cursor_field, pendulum.parse(self._start_date).int_timestamp)
        return {self.cursor_field: max(new_value, old_value)}

    def get_stream_state_value(self, stream_state: Mapping[str, Any] = None) -> int:
        """
        Returns the state value, if exists. Otherwise, returns user defined `Start Date`.
        """
        return stream_state.get(self.cursor_field) if stream_state else pendulum.parse(self._start_date).int_timestamp

    def validate_start_time(self, requested_start_time: int, value: int = 1) -> int:
        """
        The stream returns 400 Bad Request StartTimeTooRecent when requesting tasks 1 second before now.
        Figured out during experiments that the most recent time needed for request to be successful is 3 seconds before now.
        """
        return super().validate_start_time(requested_start_time, value=3)


class TicketMetricsStateMigration(StateMigration):
    """
    TicketMetrics' state cursor field has updated from `generated_timestamp` to `_ab_updated_at` with connector v4.3.0.
    In order to avoid a breaking change due to the change in the state cursor field, TicketMetrics will check
    for the streams' state and change the cursor field, if needed. The cursor datatype for both `generated_timestamp` and `_ab_updated_at` is an integer timestamp.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "generated_timestamp" in stream_state

    def migrate(self, stream_state: Optional[Mapping[str, Any]]) -> Mapping[str, Any]:
        if not stream_state:
            return stream_state
        if not self.should_migrate(stream_state):
            return stream_state
        updated_state = copy.deepcopy(stream_state)
        del updated_state["generated_timestamp"]
        updated_state["_ab_updated_at"] = stream_state["generated_timestamp"]

        return updated_state


class TicketMetrics(SourceZendeskSupportStream):
    name = "ticket_metrics"
    cursor_field = "_ab_updated_at"
    should_checkpoint = False

    def __init__(self, subdomain: str, start_date: str, ignore_pagination: bool = False, **kwargs):
        super().__init__(subdomain=subdomain, start_date=start_date, ignore_pagination=ignore_pagination, **kwargs)
        self._state_migrator = TicketMetricsStateMigration()
        self._implemented_stream: Union[StatelessTicketMetrics, StatefulTicketMetrics] = None
        self._stateless_ticket_metrics = StatelessTicketMetrics(
            subdomain=subdomain, start_date=start_date, ignore_pagination=ignore_pagination, **kwargs
        )
        self._stateful_ticket_metrics = StatefulTicketMetrics(
            parent=Tickets(subdomain=subdomain, start_date=start_date, ignore_pagination=ignore_pagination, **kwargs),
            subdomain=subdomain,
            start_date=start_date,
            ignore_pagination=ignore_pagination,
            **kwargs,
        )

    @property
    def implemented_stream(self):
        return self._implemented_stream

    @implemented_stream.setter
    def implemented_stream(self, stream):
        self._implemented_stream = stream

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def _get_implemented_stream(self, stream_state: Mapping[str, Any]) -> SourceZendeskSupportStream:
        return self._stateful_ticket_metrics if stream_state else self._stateless_ticket_metrics

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.implemented_stream._get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self.state = self._state_migrator.migrate(stream_state)
        self.implemented_stream = self._get_implemented_stream(self.state)
        yield from self.implemented_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=self.state)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield from self.implemented_stream.read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        )

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        yield from self.implemented_stream.parse_response(response=response, stream_state=stream_state)


class StatelessTicketMetrics(FullRefreshZendeskSupportStream):
    response_list_name: str = "ticket_metrics"
    cursor_field: str = "updated_at"
    should_checkpoint = False
    _state_cursor_field: str = "_ab_updated_at"
    _most_recently_updated_record: Mapping[str, Any] = None

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def path(self, **kwargs) -> str:
        return "ticket_metrics"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        records = response.json().get(self.response_list_name) or []

        for record in records:
            updated_at = record[self.cursor_field]
            record[self._state_cursor_field] = self.str_to_unixtime(updated_at)
            if updated_at > self._start_date:
                if not self._most_recently_updated_record or updated_at > self._most_recently_updated_record[self.cursor_field]:
                    self._most_recently_updated_record = record
                yield record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self._ignore_pagination:
            return None

        meta = response.json().get("meta", {}) if response.content else {}
        return {"page[after]": meta.get("after_cursor")} if meta.get("has_more") else None

    def _get_updated_state(self, current_stream_state: Mapping[str, Any], latest_record: Optional[Mapping[str, Any]]) -> Mapping[str, Any]:
        if self._most_recently_updated_record:
            new_state_value: int = (self._most_recently_updated_record or {}).get(
                self._state_cursor_field, self.str_to_unixtime(self._start_date)
            )
            stream_state = {self._state_cursor_field: new_state_value}
        else:
            stream_state = {}
        return stream_state


class StatefulTicketMetrics(HttpSubStream, IncrementalZendeskSupportStream):
    response_list_name: str = "ticket_metric"
    _state_cursor_field: str = "_ab_updated_at"
    _legacy_cursor_field: str = "generated_timestamp"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return f"tickets/{stream_slice['ticket_id']}/metrics"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        cursor_value = (stream_state or {}).get(self._state_cursor_field, self.str_to_unixtime(self._start_date))
        parent_stream_state = {self.parent.cursor_field: cursor_value}
        parent_records = self.parent.read_records(
            sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_slice=None, stream_state=parent_stream_state
        )

        for record in parent_records:
            yield {
                "ticket_id": record["id"],
                self._state_cursor_field: record.get(self._legacy_cursor_field),
            }

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        old_value = (current_stream_state or {}).get(self._state_cursor_field, self.str_to_unixtime(self._start_date))
        new_value = (latest_record or {}).get(self._state_cursor_field, self.str_to_unixtime(self._start_date))
        return {self._state_cursor_field: max(new_value, old_value)}

    def get_error_handler(self) -> Optional[ErrorHandler]:
        error_mapping = DEFAULT_ERROR_MAPPING | {
            403: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Please ensure the authenticated user has access to stream: {self.name}. If the issue persists, contact Zendesk support.",
            ),
            404: ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message="Not found. Ticket was deleted. If the issue persists, contact Zendesk support.",
            ),
        }
        return HttpStatusErrorHandler(logger=self.logger, max_retries=10, error_mapping=error_mapping)

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Iterable[Mapping]:
        record = response.json().get(self.response_list_name) or {}
        if record:
            record[self._state_cursor_field] = (stream_slice or {}).get(self._state_cursor_field)
            yield record


class TicketComments(SourceZendeskSupportTicketEventsExportStream):
    """
    Fetch the TicketComments incrementally from TicketEvents Export stream
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
        params = {
            "start_time": self.get_stream_state_value(stream_state),
            "page[size]": self.page_size,
            "sort_by": "created_at",
        }
        if next_page_token:
            params.update(next_page_token)
        return params


class TicketFields(SourceZendeskSupportStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(TimeBasedPaginationZendeskSupportStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms"""


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
            "start_time": self.get_stream_state_value(stream_state),
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
    page_size = 200
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
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes.GATEWAY_TIMEOUT:
                self.logger.error(f"Skipping stream `{self.name}`. Timed out waiting for response: {e.response.text}...")
            else:
                raise e

    def _validate_response(self, response: requests.Response, stream_state: Mapping[str, Any]) -> bool:
        """
        Ticket Audits endpoint doesn't allow filtering by date, but all data sorted by descending.
        This method used to stop making requests once we receive a response with cursor value greater than actual cursor.
        This action decreases sync time as we don't filter extra records in parse response.
        """
        data = response.json().get(self.response_list_name, [{}])
        created_at = data[0].get(self.cursor_field, "")
        cursor_date = (stream_state or {}).get(self.cursor_field) or self._start_date
        return created_at >= cursor_date

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Optional[Mapping[str, Any]]], Iterable[StreamData]
        ],
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            request, response = self._fetch_next_page(stream_slice, stream_state, next_page_token)
            yield from records_generator_fn(request, response, stream_state, stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True
            if not self._validate_response(response, stream_state):
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []


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


class Triggers(CursorPaginationZendeskSupportStream):
    """Triggers stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/triggers/#list-ticket-triggers"""


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


class UserIdentities(Users):
    """
    User Identities Stream: https://developer.zendesk.com/api-reference/ticketing/users/user_identities/

    Side-loading (https://developer.zendesk.com/documentation/ticketing/using-the-zendesk-api/side_loading/) the users stream
    (https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-user-export)
    """

    response_list_name = "identities"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        req_params = super().request_params(stream_state, stream_slice, next_page_token)
        req_params["include"] = "identities"
        return req_params


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
    next_page_field: str = "next_page"

    def path(self, **kwargs) -> str:
        return "help_center/incremental/articles"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"sort_by": "updated_at", "sort_order": "asc", **super().request_params(stream_state, stream_slice, next_page_token)}


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


class Categories(FullRefreshZendeskSupportStream):
    """Categories stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/categories/#list-categories"""


class Sections(FullRefreshZendeskSupportStream):
    """Sections stream: https://developer.zendesk.com/api-reference/help_center/help-center-api/sections/#list-sections"""
