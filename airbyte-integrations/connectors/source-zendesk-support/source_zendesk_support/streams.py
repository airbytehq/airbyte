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


from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.models import SyncMode
import requests
import types
from enum import Enum, auto
import pytz
from datetime import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from urllib.parse import parse_qsl, urlparse


DATATIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class SourceZendeskSupportStream(HttpStream, ABC):
    """"Basic Zendesk class"""

    primary_key = 'id'

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
        next_page = response.json()['next_page']
        # TODO test page
        # next_page = """https://foo.zendesk.com/api/v2/search.json?query=\"type:Group hello\"\u0026sort_by=created_at\u0026sort_order=desc\u0026page=2"""
        if next_page:
            raise Exception(dict(parse_qsl(urlparse(next_page).query)).get('page'))
            return dict(parse_qsl(urlparse(next_page).query)).get('page')
        return None


    @staticmethod
    def str2datetime(s):
        """convert string to datetime object"""
        return datetime.strptime(s, DATATIME_FORMAT)

    @staticmethod
    def datetime2str(dt):
        """convert string to datetime object"""
        return datetime.strftime(
                    dt.replace(tzinfo=pytz.UTC),
                    DATATIME_FORMAT
        )
    

class UserSettingsStream(SourceZendeskSupportStream):
    """Stream for checking of a request token and permissions"""

    def path(self, *args, **kwargs) -> str:
        return 'account/settings.json'

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""
        yield from [response.json().get('settings') or {}]

    def get_settings(self) -> Tuple[Mapping[str, Any], Union[str, None]]:
        for resp in self.read_records(SyncMode.full_refresh):
            return resp, None
        return None, "not found settings"


class IncrementalBasicSearchStream(SourceZendeskSupportStream, ABC):
    """Base class for all data lists with increantal stream"""
    
    # max size of one data chunk. 100 is limitation of ZenDesk
    state_checkpoint_interval = 100
    
    # default sorted field
    cursor_field = 'updated_at'

    def __init__(self, start_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the custom value for skiping of not relevant records
        self._start_date = self.str2datetime(start_date)

    def _prepare_query(self, updated_after: datetime = None):
        """some ZenDesk provides the field 'query' where we can send more details filter information"""
        conds = [f'type:{self.entity_type[:-1]}']
        conds.append('created>%s' % self.datetime2str(self._start_date))
        if updated_after:
            conds.append('updated>%s' % self.datetime2str(updated_after))
        return {
            'query': ' '.join(conds)
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = self._parse_next_page_number(response)
        if next_page:
            return {'next_page': next_page}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Root of all responses of searching endpoints is 'results'
        yield from response.json()['results'] or []

    def path(self, *args, **kargs) -> str:
        return 'search.json'

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        updated_after = None
        if stream_state and stream_state.get(self.cursor_field):
            updated_after = self.str2datetime(stream_state[self.cursor_field])

        # add the 'query' parameter
        res = self._prepare_query(updated_after)
        res.update({
            'sort_by': 'created_at',
            'sort_order': 'asc',
            'size': self.state_checkpoint_interval,
        })
        if next_page_token:
            res['page'] = next_page_token['next_page']
        return res

    def get_updated_state(self,
                          current_stream_state: MutableMapping[str, Any],
                          latest_record: Mapping[str, Any]
                          ) -> Mapping[str, Any]:
        # try to save maximum value of a cursor field
        return {
            self.cursor_field: max(
                (latest_record or {}).get(self.cursor_field, ""),
                (current_stream_state or {}).get(self.cursor_field, "")
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
        return f'{self.entity_type}.json'


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API AS IS"""
        yield from response.json()[self.response_list_name or self.entity_type] or []



class IncrementalBasicUnsortedStream(IncrementalBasicEntityStream, ABC):
    """basic stream for loading without sorting

       Some endpoints don't provide approachs for data filtration
       We can load all reconds fully and select updated data only
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For saving of a last stream value. Not all functions provides this value
        self._cursor_date = None
        # Flag for marking of completed process
        self._finished = False
        # For saving of a relevant last updated date
        self._max_cursor_date = None

    def _save_cursor_state(self, state: Mapping[str, Any] = None):
        """need to save stream state for some internal logic"""
        if not self._cursor_date and state and state.get(self.cursor_field):
            self._cursor_date = self.str2datetime(state[self.cursor_field])
        return

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        self._save_cursor_state(stream_state)
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """try to select relevent data only"""
    
        records = response.json()[self.response_list_name or self.entity_type] or []

        # filter by start date
        records = [record for record in records if self.str2datetime(record['created_at']) >= self._start_date]
        if not records:
            # mark as finished process. All needed data was loaded
            self._finished = True
        send_cnt = 0
        for record in records:
            updated = self.str2datetime(record[self.cursor_field])
            if not self._max_cursor_date or self._max_cursor_date < updated:
                self._max_cursor_date = updated
            if not self._cursor_date or updated > self._cursor_date:
                send_cnt += 1
                yield from [record]
        if not send_cnt:
            self._finished = True
        yield from []

    def get_updated_state(self,
                          current_stream_state: MutableMapping[str, Any],
                          latest_record: Mapping[str, Any]
                          ) -> Mapping[str, Any]:
        max_updated_at = self.datetime2str(self._max_cursor_date) if self._max_cursor_date else ''
        return {
            self.cursor_field: max(
                max_updated_at,
                (current_stream_state or {}).get(self.cursor_field, "")
            )
        }

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
        if self.is_finished or not next_page:
            return None
        return {
            'next_page': next_page
        }

    def request_params(
        self, stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        res = super().request_params(stream_state, next_page_token)
        res['page'] = (next_page_token or {}).get('next_page') or 1
        return res


class FullRefreshBasicStream(IncrementalBasicUnsortedPageStream, ABC):
    """"Basic stream for endpoints where there are not any created_at or updated_at fields"""
    state_checkpoint_interval = None


class IncrementalBasicSortedCursorStream(IncrementalBasicUnsortedStream, ABC):
    """basic stream for loading sorting data with cursor hashed pagination
    """

    def request_params(
        self, stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs
    ) -> MutableMapping[str, Any]:
        res = super().request_params(stream_state, next_page_token)
        self._save_cursor_state(stream_state)
        res.update({
            'sort_by': self.cursor_field,
            'sort_order': 'desc',
        })
        return res

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.is_finished:
            return None
        before_cursor = response.json()['before_cursor']

        if before_cursor:
              return {'before_cursor': before_cursor}
        return None

class IncrementalBasicSortedPageStream(IncrementalBasicUnsortedPageStream, ABC):
    """basic stream for loading sorting data with normal pagination
    """

    def request_params(
        self, stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs
    ) -> MutableMapping[str, Any]:

        self._save_cursor_state(stream_state)
        res = {
            'sort_by': self.cursor_field,
            'sort_order': 'desc',
            'limit': self.state_checkpoint_interval
        }
        
        if (next_page_token or {}).get('before_cursor'):
            res['cursor'] = next_page_token['before_cursor']
        return res



class CustomTicketAuditsStream(IncrementalBasicSortedCursorStream, ABC):
    """Custom class for ticket_audits logic because a data response has not standard struct"""
    # ticket audits doesn't have the 'updated_by' field
    cursor_field = 'created_at'

    # Root of response is 'audits'. As rule as an endpoint name is equel a response list name
    response_list_name = 'audits'


class CustomCommentsStream(IncrementalBasicSortedPageStream, ABC):
    """Custom class for ticket_comments logic because ZenDesk doesn't provide API
       for loading of all comment by one direct endpoints. Thus at first we loads
       all updated tickets and after this tries to load all created/updated comment
       per every ticket"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Flag of loaded state. it is tickets' loaging if it is False and
        #  it is comments' loaging if it is vice versa
        self._loaded = False
        # Array for ticket IDs 
        self._ticket_ids = deque()


    def path(self, *args, **kwargs) -> str:
        if not self._loaded:
            return 'tickets.json'
        return f'tickets/{self._ticket_ids[-1]}/comments.json'


    def request_params(
        self, stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        **kwargs
    ) -> MutableMapping[str, Any]:
        res = super().request_params(stream_state, next_page_token)
        if not self._loaded:
            res['include'] = 'comment_count'

        return res


    @property
    def response_list_name(self):
        if not self._loaded:
            return 'tickets'
        return 'comments'


    @property
    def cursor_field(self):
        if self._loaded:
            return 'created_at'
        return super().cursor_field

        
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """try to select relevent data only"""
        if self._loaded:
            yield from super().parse_response(response, **kwargs)
        else:
            for record in super().parse_response(response, **kwargs):
                # will handle tickets with commonts only
                if record['comment_count']:
                    self._ticket_ids.append(record['id'])
        yield from []
        

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        res = super().next_page_token(response)
        if res is not None or not len(self._ticket_ids):
            return res
        
        if self._loaded:
            self._ticket_ids.pop()
            if not len(self._ticket_ids):
                return None 
        else:
            self.logger.info(f"Found updated tickets: {list(self._ticket_ids)}")
            self._loaded = True 
        
        self._finished = False
        self._page = 1
        # self.logger.warn(str(self._ticket_ids))
        return {
            'next_page': self._page
        }


    def _save_cursor_state(self, state: Mapping[str, Any] = None):
        """need to save stream state for some internal logic"""
        if not self._cursor_date and state and (state.get('created_at') or state.get('updated_at')):
            self._cursor_date = self.str2datetime(state.get('created_at') or state['updated_at'])
        return

class CustomTagsStream(FullRefreshBasicStream, ABC):
    """Custom class for tags logic because tag data doesn't included the field 'id'"""

    primary_id = 'name'

class CustomSlaPoliciesStream(FullRefreshBasicStream, ABC):
    """Custom class for sla_policies logic because its path format is not standard"""
    def path(self, *args, **kwargs) -> str:
        return 'slas/policies.json'

ENTITY_NAMES = {
    # endpoints provide the 'query' field for more detail searching
    'users': IncrementalBasicSearchStream,
    'groups': IncrementalBasicSearchStream,
    'organizations': IncrementalBasicSearchStream,
    'tickets': IncrementalBasicSearchStream,

    # endpoints provide a pagination mechanism but we can't manage a response order
    'group_memberships': IncrementalBasicUnsortedPageStream,
    'satisfaction_ratings': IncrementalBasicUnsortedPageStream,
    'ticket_fields': IncrementalBasicUnsortedPageStream,
    'ticket_forms': IncrementalBasicUnsortedPageStream,
    'ticket_metrics': IncrementalBasicUnsortedPageStream,

    # endpoints provide a pagination and sorting mechanism
    'macros': IncrementalBasicSortedPageStream,
    'ticket_comments': CustomCommentsStream,

    # endpoints provide a cursor pagination and sorting mechanism
    'ticket_audits': CustomTicketAuditsStream,

    # endpoints dont provide the updated_at/created_at fields 
    # thus we can't implement an incremental ligic for them    
    'tags': CustomTagsStream,
    'sla_policies': CustomSlaPoliciesStream,
}


def generate_stream_classes():
    """generates target stream classes with necessary class names"""
    res = []
    for name, base_cls in ENTITY_NAMES.items():
        # snake to camel
        class_name = ''.join([w.title() for w in name.split('_')])
        class_body = {
            "__module__": __name__,
            'entity_type': name
        }
        res.append(
            types.new_class(
                class_name,
                bases=(base_cls,),
                exec_body=lambda ns: ns.update(class_body)
            )
        )
    return res

