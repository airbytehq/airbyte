#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import calendar
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class SourceZendeskException(Exception):
    """default exception of custom SourceZendesk logic"""


class SourceZendeskSupportStream(HttpStream, ABC):
    """"Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    created_at_field = "created_at"
    updated_at_field = "updated_at"

    def __init__(self, subdomain: str, **kwargs):
        super().__init__(**kwargs)

        # add the custom value for generation of a zendesk domain
        self._subdomain = subdomain

    @property
    def url_base(self) -> str:
        return f"https://{self._subdomain}.zendesk.com/api/v2/"

    @staticmethod
    def _parse_next_page_number(response: requests.Response) -> Optional[int]:
        """Parses a response and tries to find next page number"""
        next_page = response.json()["next_page"]
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
        Input example: '2021-07-22T06:55:55Z' FROMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        if not str_dt:
            return None
        return datetime.strptime(str_dt, DATETIME_FORMAT)

    @staticmethod
    def datetime2str(dt: datetime) -> str:
        """convert datetime object to string
        Output example: '2021-07-22T06:55:55Z' FROMAT : "%Y-%m-%dT%H:%M:%SZ"
        """
        return datetime.strftime(dt.replace(tzinfo=pytz.UTC), DATETIME_FORMAT)


class UserSettingsStream(SourceZendeskSupportStream):
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


class IncrementalEntityStream(SourceZendeskSupportStream, ABC):
    """Stream for endpoints where an entity name can be used in a path value
    https://<subdomain>.zendesk.com/api/v2/<self.name>.json
    """

    # default sorted field
    cursor_field = SourceZendeskSupportStream.updated_at_field

    # for partial cases when JSON root name of responses is not equal a name value
    response_list_name: str = None

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        # add the custom value for skiping of not relevant records
        self._start_date = self.str2datetime(start_date) if isinstance(start_date, str) else start_date
        # Flag for marking of completed process
        self._finished = False

    @property
    def is_finished(self):
        return self._finished

    def path(self, **kwargs) -> str:
        return f"{self.name}.json"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns a list of records"""
        # filter by start date
        for record in response.json().get(self.response_list_name or self.name) or []:
            if record.get(self.created_at_field) and self.str2datetime(record[self.created_at_field]) < self._start_date:
                continue
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        old_value = str((current_stream_state or {}).get(self.cursor_field, ""))
        new_value = str((latest_record or {}).get(self.cursor_field, ""))
        return {self.cursor_field: max(new_value, old_value)}


class IncrementalExportStream(IncrementalEntityStream, ABC):
    """Use the incremental export API to get items that changed or
    were created in Zendesk Support since the last request
    See: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/

    You can make up to 10 requests per minute to these endpoints.
    """

    # maximum of 1,000
    page_size = 1000

    # try to save a stage after every 100 records
    # this endpoint provides responces in ascending order.
    state_checkpoint_interval = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # for saving of last page cursor value
        # endpoints can have different cursor format but incremental logic uses unixtime format only
        self._last_end_time = None

    @staticmethod
    def str2unixtime(str_dt: str) -> int:
        """convert string to unixtime number
        Input example: '2021-07-22T06:55:55Z' FROMAT : "%Y-%m-%dT%H:%M:%SZ"
        Output example: 1626936955"
        """
        if not str_dt:
            return None
        dt = datetime.strptime(str_dt, DATETIME_FORMAT)
        return calendar.timegm(dt.utctimetuple())

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_finished:
            return None
        return {"start_time": self._last_end_time}

    def path(self, *args, **kwargs) -> str:
        return f"incremental/{self.name}.json"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_size}
        if not next_page_token:
            current_state = stream_state.get("_last_end_time")
            if not current_state:
                # try to search all reconds with generated_timestamp > start_time
                current_state = stream_state.get(self.cursor_field)
                if current_state and isinstance(current_state, str) and not current_state.isdigit():
                    current_state = self.str2unixtime(current_state)

            start_time = int(current_state or time.mktime(self._start_date.timetuple()))
            # +1 because the API returns all records where  generated_timestamp >= start_time

            now = calendar.timegm(datetime.now().utctimetuple())
            if start_time > now - 60:
                # start_time must be more than 60 seconds ago
                start_time = now - 61
            params["start_time"] = start_time

        else:
            params.update(next_page_token)
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        state = super().get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)

        if self._last_end_time:
            state["_last_end_time"] = self._last_end_time
        current_stream_state.update(state)
        return current_stream_state

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:

        data = response.json()
        # save a last end time for the next attempt
        self._last_end_time = data["end_time"]
        # end_of_stream is true if the current request has returned all the results up to the current time; false otherwise
        self._finished = data["end_of_stream"]
        yield from super().parse_response(response, stream_state=stream_state, stream_slice=stream_slice, **kwargs)


class IncrementalUnsortedStream(IncrementalEntityStream, ABC):
    """Stream for loading without sorting

    Some endpoints don't provide approachs for data filtration
    We can load all reconds fully and select updated data only
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # For saving of a relevant last updated date
        self._max_cursor_date = None

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """try to select relevant data only"""

        if not self.cursor_field:
            yield from super().parse_response(response, stream_state=stream_state, **kwargs)
        else:
            send_cnt = 0
            cursor_date = (stream_state or {}).get(self.cursor_field)
            for record in super().parse_response(response, stream_state=stream_state, **kwargs):
                updated = record[self.cursor_field]
                if not self._max_cursor_date or self._max_cursor_date < updated:
                    self._max_cursor_date = updated
                if not cursor_date or updated > cursor_date:
                    send_cnt += 1
                    yield record
            if not send_cnt:
                self._finished = True

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(self._max_cursor_date or "", (current_stream_state or {}).get(self.cursor_field, ""))}

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """can be different for each case"""


class IncrementalUnsortedPageStream(IncrementalUnsortedStream, ABC):
    """Stream for loading without sorting but with pagination
    This logic can be used for a small data size when this data is loaded fast
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = self._parse_next_page_number(response)
        if not next_page:
            self._finished = True
            return None
        return next_page

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params["page"] = next_page_token or 1
        return params


class FullRefreshStream(IncrementalUnsortedPageStream, ABC):
    """"Stream for endpoints where there are not any created_at or updated_at fields"""

    # reset to default value
    cursor_field = SourceZendeskSupportStream.cursor_field


class IncrementalSortedCursorStream(IncrementalUnsortedStream, ABC):
    """Stream for loading sorting data with cursor based pagination"""

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size})

        if next_page_token:
            params["cursor"] = next_page_token
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_finished:
            return None
        return response.json().get("before_cursor")


class IncrementalSortedPageStream(IncrementalUnsortedPageStream, ABC):
    """Stream for loading sorting data with normal pagination"""

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        if params:
            params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.page_size})
        return params


class TicketComments(IncrementalSortedPageStream):
    """TicketComments stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_comments/
    ZenDesk doesn't provide API for loading of all comments by one direct endpoints.
    Thus at first we loads all updated tickets and after this tries to load all created/updated
    comments per every ticket"""

    response_list_name = "comments"
    cursor_field = IncrementalSortedPageStream.created_at_field

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # need to save a slice ticket state
        # because the function get_updated_state doesn't have a stream_slice as argument
        self._slice_cursor_date = None

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ticket_id = stream_slice["id"]
        return f"tickets/{ticket_id}/comments.json"

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        # save a slice ticket state
        self._cursor_ticket_date = stream_slice[Tickets.cursor_field]
        yield from super().parse_response(response, stream_state=stream_state, stream_slice=stream_slice, **kwargs)

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Loads all updated tickets after last stream state"""
        stream_state = stream_state or {}
        # convert a comment state value to a ticket one
        # tickets and comments have different cursor formats. For example:
        # Ticket state {"generated_timestamp": 1627637409}
        # Comment state: {"created_at": "2021-07-30T12:30:09Z"}
        # At the first try to find a ticket cursor value
        ticket_stream_value = stream_state.get(Tickets.cursor_field)
        if not ticket_stream_value:
            # for backward compatibility because not all relevant states can have some last ticket state
            ticket_stream_value = Tickets.str2unixtime(stream_state.get(self.cursor_field))

        tickets = Tickets(start_date=self._start_date, subdomain=self._subdomain, authenticator=self.authenticator).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_state={Tickets.cursor_field: ticket_stream_value}
        )

        # selects all tickets what have at least one comment
        ticket_ids = [
            {
                "id": ticket["id"],
                Tickets.cursor_field: ticket[Tickets.cursor_field],
            }
            for ticket in tickets
            if ticket["comment_count"]
        ]
        self.logger.info(f"Found updated {len(ticket_ids)} ticket(s) with comments")
        # sort slices by generated_timestamp
        ticket_ids.sort(key=lambda ticket: ticket[Tickets.cursor_field])
        return ticket_ids

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """Adds a last cursor ticket updated time for a comment state"""
        new_state = super().get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)
        if new_state:
            new_state[Tickets.cursor_field] = self._cursor_ticket_date
        return new_state


# NOTE: all Zendesk endpoints can be splitted into several templates of data loading.
# 1) with API built-in incremental approach
# 2)  pagination and sorting mechanism
# 3) cursor pagination and sorting mechanism
# 4) without sorting but with pagination
# 5) without created_at/updated_at fields

# endpoints provide a built-in incremental approach
class Users(IncrementalExportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Organizations(IncrementalExportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Tickets(IncrementalExportStream):
    """Tickets stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""

    # The API compares the start_time with the ticket's generated_timestamp value, not its updated_at value.
    # The generated_timestamp value is updated for all entity updates, including system updates.
    # If a system update occurs after a event, the unchanged updated_at time will become earlier relative to the updated generated_timestamp time.
    cursor_field = "generated_timestamp"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """Save state as integer"""
        state = super().get_updated_state(current_stream_state, latest_record)
        if state:
            state[self.cursor_field] = int(state[self.cursor_field])
        return state

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Adds the field 'comment_count'"""
        params = super().request_params(**kwargs)
        params["include"] = "comment_count"
        return params


# endpoints provide a pagination mechanism but we can't manage a response order


class Groups(IncrementalUnsortedPageStream):
    """Groups stream: https://developer.zendesk.com/api-reference/ticketing/groups/groups/"""


class GroupMemberships(IncrementalUnsortedPageStream):
    """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""


class SatisfactionRatings(IncrementalUnsortedPageStream):
    """SatisfactionRatings stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/satisfaction_ratings/"""


class TicketFields(IncrementalUnsortedPageStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(IncrementalUnsortedPageStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms/"""


class TicketMetrics(IncrementalUnsortedPageStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""


# endpoints provide a pagination and sorting mechanism


class Macros(IncrementalSortedPageStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


# endpoints provide a cursor pagination and sorting mechanism


class TicketAudits(IncrementalSortedCursorStream):
    """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""

    # can request a maximum of 1,000 results
    page_size = 1000
    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"


# endpoints dont provide the updated_at/created_at fields
# thus we can't implement an incremental logic for them


class Tags(FullRefreshStream):
    """Tags stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/"""

    # doesn't have the 'id' field
    primary_key = "name"


class SlaPolicies(FullRefreshStream):
    """SlaPolicies stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"
