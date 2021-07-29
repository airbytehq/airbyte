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
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
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

    @property
    def entity_type(self):
        """for generation of a path value and as rule as JSON root name of all response
        Can be changed for some cases
        """
        return self.name

    def __init__(self, subdomain: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def backoff_time(self, response: requests.Response):
        """
        The rate limit is 700 requests per minute
        # monitoring-your-request-activity
        See https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/
        The response has a Retry-After header that tells you for how many seconds to wait before retrying.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            return int(retry_after)
        # the header X-Rate-Limit returns a amount of requests per minute
        # we try to wait twice as long
        rate_limit = float(response.headers.get("X-Rate-Limit") or 0)
        if rate_limit:
            return (60.0 / rate_limit) * 2
        # default value if there is not any headers
        return 60

    @staticmethod
    def str2datetime(s):
        """convert string to datetime object"""
        if not s:
            return None
        return datetime.strptime(s, DATETIME_FORMAT)

    @staticmethod
    def datetime2str(dt):
        """convert datetime object to string"""
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
        yield from [response.json().get("settings") or {}]

    def get_settings(self) -> Tuple[Mapping[str, Any], Union[str, None]]:
        for resp in self.read_records(SyncMode.full_refresh):
            return resp
        raise SourceZendeskException("not found settings")


class IncrementalBasicEntityStream(SourceZendeskSupportStream, ABC):
    """basic stream for endpoints where an entity name can be used in a path value
    https://<subdomain>.zendesk.com/api/v2/<entity_name>.json
    """

    # max size of one data chunk. 100 is limitation of ZenDesk
    state_checkpoint_interval = SourceZendeskSupportStream.page_size

    # default sorted field
    cursor_field = SourceZendeskSupportStream.updated_at_field

    # for partial cases when JSON root name of responses is not equal a entity_type value
    response_list_name: str = None

    def __init__(self, start_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the custom value for skiping of not relevant records
        self._start_date = self.str2datetime(start_date) if isinstance(start_date, str) else start_date

    def path(self, *args, **kwargs) -> str:
        return f"{self.entity_type}.json"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """returns a list of records"""
        self.logger.info(
            "request activity %s/%s" % (response.headers.get("X-Rate-Limit-Remaining", 0), response.headers.get("X-Rate-Limit", 0))
        )

        # filter by start date
        for record in response.json().get(self.response_list_name or self.entity_type) or []:
            if record.get(self.created_at_field) and self.str2datetime(record[self.created_at_field]) < self._start_date:
                continue
            yield record
        yield from []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        return {
            self.cursor_field: max(
                str((latest_record or {}).get(self.cursor_field, "")), str((current_stream_state or {}).get(self.cursor_field, ""))
            )
        }


class IncrementalBasicExportStream(IncrementalBasicEntityStream, ABC):
    """Use the incremental export API to get items that changed or
    were created in Zendesk Support since the last request
    See: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/

    You can make up to 10 requests per minute to these endpoints.
    """

    # maximum of 1,000
    page_size = 1000

    @staticmethod
    def str2unixtime(s):
        """convert string to unixtime number"""
        if not s:
            return None
        dt = datetime.strptime(s, DATETIME_FORMAT)
        return calendar.timegm(dt.utctimetuple())

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if data["end_of_stream"]:
            # true if the current request has returned all the results up to the current time; false otherwise
            return None

        return {"start_time": data["end_time"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()[self.entity_type] or []

    def path(self, *args, **kwargs) -> str:
        return f"incremental/{self.entity_type}.json"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:

        params = {"per_page": self.page_size}
        if not next_page_token:
            # try to search all reconds with generated_timestamp > start_time
            current_state = stream_state.get(self.cursor_field)
            if current_state and isinstance(current_state, str) and not current_state.isdigit():
                # try to save a stage with UnixTime format
                current_state = self.str2unixtime(current_state)
            start_time = int(current_state or time.mktime(self._start_date.timetuple())) + 1
            now = calendar.timegm(datetime.now().utctimetuple())
            if start_time > now - 60:
                # start_time must be more than 60 seconds ago
                start_time = now - 61
            params["start_time"] = start_time
            # +1 because the API returns all records where  generated_timestamp >= start_time
        else:
            params.update(next_page_token)
        return params


class IncrementalBasicUnsortedStream(IncrementalBasicEntityStream, ABC):
    """basic stream for loading without sorting

    Some endpoints don't provide approachs for data filtration
    We can load all reconds fully and select updated data only
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Flag for marking of completed process
        self._finished = False
        # For saving of a relevant last updated date
        self._max_cursor_date = None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        return {}

    def _get_stream_date(self, stream_state: Mapping[str, Any], **kwargs) -> datetime:
        """Can change a date of comparison"""
        return self.str2datetime((stream_state or {}).get(self.cursor_field))

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """try to select relevant data only"""
        # monitoring of a request activity
        # https://developer.zendesk.com/api-reference/ticketing/account-configuration/usage_limits/
        if not self.cursor_field:
            yield from super().parse_response(response, stream_state, **kwargs)
        else:
            send_cnt = 0
            cursor_date = self._get_stream_date(stream_state, **kwargs)
            for record in super().parse_response(response, stream_state, **kwargs):
                updated = self.str2datetime(record[self.cursor_field])
                if not self._max_cursor_date or self._max_cursor_date < updated:
                    self._max_cursor_date = updated
                if not cursor_date or updated > cursor_date:
                    send_cnt += 1
                    yield record
            if not send_cnt:
                self._finished = True
        yield from []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        max_updated_at = self.datetime2str(self._max_cursor_date) if self._max_cursor_date else ""
        return {self.cursor_field: max(max_updated_at, (current_stream_state or {}).get(self.cursor_field, ""))}

    @property
    def is_finished(self):
        return self._finished

    @abstractmethod
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """can be different for each case"""


class IncrementalBasicUnsortedPageStream(IncrementalBasicUnsortedStream, ABC):
    """basic stream for loading without sorting but with pagination
    This logic can be used for a small data size when this data is loaded fast
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = self._parse_next_page_number(response)
        if not next_page:
            self._finished = True
            return None
        return next_page

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token)
        params["page"] = next_page_token or 1
        return params


class FullRefreshBasicStream(IncrementalBasicUnsortedPageStream, ABC):
    """"Basic stream for endpoints where there are not any created_at or updated_at fields"""

    state_checkpoint_interval = None
    cursor_field = []


class IncrementalBasicSortedCursorStream(IncrementalBasicUnsortedStream, ABC):
    """basic stream for loading sorting data with cursor based pagination"""

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token)
        params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.state_checkpoint_interval})

        if next_page_token:
            params["cursor"] = next_page_token
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_finished:
            return None
        return response.json().get("before_cursor")


class IncrementalBasicSortedPageStream(IncrementalBasicUnsortedPageStream, ABC):
    """basic stream for loading sorting data with normal pagination"""

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        if params:
            params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.state_checkpoint_interval})
        return params


class TicketComments(IncrementalBasicSortedPageStream):
    """TicketComments stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_comments/
    ZenDesk doesn't provide API for loading of all comments by one direct endpoints.
    Thus at first we loads all updated tickets and after this tries to load all created/updated
    comments per every ticket"""

    response_list_name = "comments"
    cursor_field = IncrementalBasicSortedPageStream.created_at_field

    class Tickets(IncrementalBasicSortedPageStream):
        def request_params(
            self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
        ) -> MutableMapping[str, Any]:
            """Adds the field 'comment_count' for skipping tickets without comment"""
            params = super().request_params(stream_state, next_page_token)
            params["include"] = "comment_count"
            return params

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        ticket_id = stream_slice["id"]
        return f"tickets/{ticket_id}/comments.json"

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Loads all updated tickets after last stream state"""
        stream_state = stream_state or {}
        tickets = self.Tickets(self._start_date, subdomain=self._subdomain, authenticator=self.authenticator).read_records(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_state={self.updated_at_field: stream_state.get(self.cursor_field)}
        )
        # selects all tickets what have at least one comment
        stream_state = self.str2datetime(stream_state.get(self.cursor_field))
        ticket_ids = [
            {
                "id": ticket["id"],
                "start_stream_state": stream_state,
            }
            for ticket in tickets
            if ticket["comment_count"]
        ]
        self.logger.info(f"Found updated tickets with comments: {[t['id'] for t in  ticket_ids]}")
        return reversed(ticket_ids)

    def _get_stream_date(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> datetime:
        """For each tickets all comments must be compared with a start value of stream state"""
        return stream_slice["start_stream_state"]


# NOTE: all Zendesk endpoints can be splitted into several templates of data loading.
# 1) with query parameter
# 2)  pagination and sorting mechanism
# 3) cursor pagination and sorting mechanism
# 4) without sorting but with pagination
# 5) without created_at/updated_at fields

# endpoints provide the 'query' field for more detail searching
class Users(IncrementalBasicExportStream):
    """Users stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Organizations(IncrementalBasicExportStream):
    """Organizations stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/"""


class Tickets(IncrementalBasicExportStream):
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


# endpoints provide a pagination mechanism but we can't manage a response order


class Groups(IncrementalBasicUnsortedPageStream):
    """Groups stream: https://developer.zendesk.com/api-reference/ticketing/groups/groups/"""


class GroupMemberships(IncrementalBasicUnsortedPageStream):
    """GroupMemberships stream: https://developer.zendesk.com/api-reference/ticketing/groups/group_memberships/"""


class SatisfactionRatings(IncrementalBasicUnsortedPageStream):
    """SatisfactionRatings stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/satisfaction_ratings/"""


class TicketFields(IncrementalBasicUnsortedPageStream):
    """TicketFields stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_fields/"""


class TicketForms(IncrementalBasicUnsortedPageStream):
    """TicketForms stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_forms/"""


class TicketMetrics(IncrementalBasicUnsortedPageStream):
    """TicketMetric stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_metrics/"""


# endpoints provide a pagination and sorting mechanism


class Macros(IncrementalBasicSortedPageStream):
    """Macros stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/macros/"""


# endpoints provide a cursor pagination and sorting mechanism


class TicketAudits(IncrementalBasicSortedCursorStream):
    """TicketAudits stream: https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/"""

    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"


# endpoints dont provide the updated_at/created_at fields
# thus we can't implement an incremental logic for them


class Tags(FullRefreshBasicStream):
    """Tags stream: https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/"""

    primary_key = "name"


class SlaPolicies(FullRefreshBasicStream):
    """SlaPolicies stream: https://developer.zendesk.com/api-reference/ticketing/business-rules/sla_policies/"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"
