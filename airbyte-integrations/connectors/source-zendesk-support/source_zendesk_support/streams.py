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


import types
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse

import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class SourceZendeskSupportStream(HttpStream, ABC):
    """"Basic Zendesk class"""

    primary_key = "id"

    page_size = 100
    created_at_field = "created_at"
    updated_at_field = "updated_at"

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
        # TODO test page
        # next_page = """https://foo.zendesk.com/api/v2/search.json?page=2"""
        if next_page:
            return dict(parse_qsl(urlparse(next_page).query)).get("page")
        return None

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
            return resp, None
        return None, "not found settings"


class IncrementalBasicSearchStream(SourceZendeskSupportStream, ABC):
    """Base class for all data lists with a incremental stream"""

    # max size of one data chunk. 100 is limitation of ZenDesk
    state_checkpoint_interval = SourceZendeskSupportStream.page_size

    # default sorted field
    cursor_field = SourceZendeskSupportStream.updated_at_field

    def __init__(self, start_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the custom value for skiping of not relevant records
        self._start_date = self.str2datetime(start_date) if isinstance(start_date, str) else start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = self._parse_next_page_number(response)
        if next_page:
            return {"next_page": next_page}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Root of all responses of searching endpoints is 'results'
        yield from response.json()["results"] or []

    def path(self, *args, **kargs) -> str:
        return "search.json"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        updated_after = None
        if stream_state and stream_state.get(self.cursor_field):
            updated_after = self.str2datetime(stream_state[self.cursor_field])

        # add the 'query' parameter
        conds = [f"type:{self.entity_type[:-1]}"]
        conds.append("created>%s" % self.datetime2str(self._start_date))
        if updated_after:
            conds.append("updated>%s" % self.datetime2str(updated_after))

        res = {
            "query": " ".join(conds),
            "sort_by": self.updated_at_field,
            "sort_order": "desc",
            "size": self.state_checkpoint_interval,
        }
        if next_page_token:
            res["page"] = next_page_token["next_page"]
        return res

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        return {
            self.cursor_field: max(
                (latest_record or {}).get(self.cursor_field, ""), (current_stream_state or {}).get(self.cursor_field, "")
            )
        }


class IncrementalBasicEntityStream(IncrementalBasicSearchStream, ABC):
    """basic stream for endpoints where an entity name can be used in a path value
    https://<subdomain>.zendesk.com/api/v2/<entity_name>.json
    """

    # for generation of a path value and as rule as JSON root name of all response
    entity_type: str = None

    # for partial cases when JSON root name of responses is not equal a entity_type value
    response_list_name: str = None

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
        return {"next_page": next_page}

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token)
        params["page"] = (next_page_token or {}).get("next_page") or 1
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
        before_cursor = (next_page_token or {}).get("before_cursor")
        if before_cursor:
            params["cursor"] = before_cursor
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_finished:
            return None
        before_cursor = response.json().get("before_cursor")

        if before_cursor:
            return {"before_cursor": before_cursor}
        return None


class IncrementalBasicSortedPageStream(IncrementalBasicUnsortedPageStream, ABC):
    """basic stream for loading sorting data with normal pagination"""

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, next_page_token, **kwargs)
        if params:
            params.update({"sort_by": self.cursor_field, "sort_order": "desc", "limit": self.state_checkpoint_interval})
        return params


class CustomTicketAuditsStream(IncrementalBasicSortedCursorStream, ABC):
    """Custom class for ticket_audits logic because a data response has not standard struct"""

    # ticket audits doesn't have the 'updated_by' field
    cursor_field = "created_at"

    # Root of response is 'audits'. As rule as an endpoint name is equal a response list name
    response_list_name = "audits"


class CustomCommentsStream(IncrementalBasicSortedPageStream, ABC):
    """Custom class for ticket_comments logic because ZenDesk doesn't provide API
    for loading of all comments by one direct endpoints. Thus at first we loads
    all updated tickets and after this tries to load all created/updated comment
    per every ticket"""

    response_list_name = "comments"
    cursor_field = IncrementalBasicSortedPageStream.created_at_field

    class Tickets(IncrementalBasicSortedPageStream):
        entity_type = "tickets"

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


class CustomTagsStream(FullRefreshBasicStream, ABC):
    """Custom class for tags logic because tag data doesn't include the field 'id"""

    primary_key = "name"


class CustomSlaPoliciesStream(FullRefreshBasicStream, ABC):
    """Custom class for sla_policies logic because its path format is not standard"""

    def path(self, *args, **kwargs) -> str:
        return "slas/policies.json"


# NOTE: all Zendesk endpoints can be splitted into several templates of data loading.
# 1) with query parameter
# 2)  pagination and sorting mechanism
# 3) cursor pagination and sorting mechanism
# 4) without sorting but with pagination
# 5) without created_at/updated_at fields
ENTITY_NAMES = {
    # endpoints provide the 'query' field for more detail searching
    "users": IncrementalBasicSearchStream,
    "groups": IncrementalBasicSearchStream,
    "organizations": IncrementalBasicSearchStream,
    "tickets": IncrementalBasicSearchStream,
    # endpoints provide a pagination mechanism but we can't manage a response order
    "group_memberships": IncrementalBasicUnsortedPageStream,
    "satisfaction_ratings": IncrementalBasicUnsortedPageStream,
    "ticket_fields": IncrementalBasicUnsortedPageStream,
    "ticket_forms": IncrementalBasicUnsortedPageStream,
    "ticket_metrics": IncrementalBasicUnsortedPageStream,
    # endpoints provide a pagination and sorting mechanism
    "macros": IncrementalBasicSortedPageStream,
    "ticket_comments": CustomCommentsStream,
    # endpoints provide a cursor pagination and sorting mechanism
    "ticket_audits": CustomTicketAuditsStream,
    # endpoints dont provide the updated_at/created_at fields
    # thus we can't implement an incremental logic for them
    "tags": CustomTagsStream,
    "sla_policies": CustomSlaPoliciesStream,
}

#  sort it alphabetically
ENTITY_NAMES = {k: ENTITY_NAMES[k] for k in sorted(ENTITY_NAMES.keys())}


def generate_stream_classes():
    """generates target stream classes with necessary class names"""
    res = []
    for name, base_cls in ENTITY_NAMES.items():
        # snake to camel
        class_name = "".join([w.title() for w in name.split("_")])
        class_body = {"__module__": __name__, "entity_type": name}
        res.append(types.new_class(class_name, bases=(base_cls,), exec_body=lambda ns: ns.update(class_body)))
    return res
