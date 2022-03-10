from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.token import TokenAuthenticator


class SourceMagento(AbstractSource):

    def datereturn(datestring:str) -> datetime:
            if(datestring == ''):
                return None
            try:
                date = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
            except:
                return False

            return date

    def page_size(config) -> str:
            if 'page_size' in config:
                return config['page_size']
            else:
                return '100'


    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:

        headers_dict = {"Authorization": f"Bearer {config['magento_bearer']}"}
        params = {
            'searchCriteria[pageSize]': 1,
        }

        # Initiate Request
        req = requests.get(
            f'{config["base_url"]}orders',  # url of api
            headers=headers_dict,  # Set headers
            params=params  # set Query parameters
        )
        dates = { 
            'start_date': SourceMagento.datereturn(config['start_date']),
            'end_date' : SourceMagento.datereturn(config['end_date'])
        }

        if(isinstance(dates['start_date'], datetime) != True):
            return False, f'start_date is not valid. Please check your input: { config["start_date"] }'
        
        res = req.json()
        errors = {
            401: f'Unauthorized request. Check your credentials and permissions: {res}',
            403: f'Unauthorized request. Probably your permissions in the backend aren\'t correct: {res}',
            404: f'Route not found. Please check your base URL or submit a bug request: {res}',
            405: f'Method not allowed. Please contact your developer. Airbyte needs at least the permission to make GET requests: {res}',
        }

        if(req.status_code > 299):
            if req.status_code in errors:
                message = errors[req.status_code]
            else:
                message = f"Api token or Base Url not valid. Please check your values and credentials in the backend of Magento: {res}"

            return False, message

        return True, None

    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        
        auth = TokenAuthenticator(config['magento_bearer'])
        cursor_field = 'updated_at' if 'cursor_field_value' not in config else config['cursor_field_value']

        args = {
            'authenticator':auth,
            'start_date': SourceMagento.datereturn(config['start_date']),
            'end_date': SourceMagento.datereturn(config['end_date']),
            'base_url': config['base_url'],
            'page_size':SourceMagento.page_size(config),
            'cursor_field_value': cursor_field
        }
        return [
            SalesOrders(
                **args
            )
        ]

# Basic full refresh stream


class MagentoStream(HttpStream, ABC):

    primary_key = 'increment_id'

    def __init__(self, start_date, end_date, page_size: str, base_url: str, cursor_field_value: str,  **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date
        self.page_size = page_size
        self._cursor_value = None
        self.base_url = base_url
        self.cursor_field_value = cursor_field_value

    # Base Url depends on store
    @property
    def url_base(self) -> str:
        return self.base_url

    @property
    def state_checkpoint_interval(self) -> Optional[int]:
        return int(self.page_size)

    @property
    def cursor_field(self):
        return self.cursor_field_value

    # Pagination is always the same. Max 300 items per page
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        res = response.json()
        page = res['search_criteria']['current_page']

        total_count = res['total_count']
        page_size = res['search_criteria']['page_size']

        if (page * page_size) > total_count:
            return None

        return page + 1

    # Request params are the same for every api call.
    def request_params(self,
                       stream_state: Mapping[str, Any],
                       next_page_token: Mapping[str, Any] = None,
                       **kwargs
                       ) -> MutableMapping[str, Any]:

        if next_page_token == None:
            page = 1
        else:
            page = next_page_token

        params = {
            'searchCriteria[filter_groups][0][filters][0][field]': self.cursor_field,
            'searchCriteria[filter_groups][0][filters][0][value]': self.start_date,
            'searchCriteria[filter_groups][0][filters][0][condition_type]': 'gteq',
            'searchCriteria[pageSize]': self.page_size,
            'searchCriteria[currentPage]': page,
            'searchCriteria[sortOrders][0][field]':self.cursor_field,
            'searchCriteria[sortOrders][0][direction]':'asc'
        }
        if self.end_date:
            params = {
                **params,
                'searchCriteria[filter_groups][1][filters][0][field]': self.cursor_field,
                'searchCriteria[filter_groups][1][filters][0][value]': self.end_date,
                'searchCriteria[filter_groups][1][filters][0][condition_type]': 'lt',
            }

        return params

    # Parse the repsonse and just returns items
    def parse_response(self, response: requests.Response, *, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs) -> List:
        res = response.json()
        return res['items']


# Basic incremental stream
class IncrementalMagentoStream(MagentoStream, IncrementalMixin):

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d %H:%M:%S')}
        else:
            return {self.cursor_field: self.start_date.strftime('%Y-%m-%d %H:%M:%S')}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], '%Y-%m-%d %H:%M:%S')

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            latest_record_date = datetime.strptime(record[self.cursor_field], '%Y-%m-%d %H:%M:%S')
            if self._cursor_value:
                latest_record_date = datetime.strptime(record[self.cursor_field], '%Y-%m-%d %H:%M:%S')
                self._cursor_value = max(
                    self._cursor_value, latest_record_date)
            else:
                self._cursor_value = latest_record_date
            yield record


class SalesOrders(IncrementalMagentoStream):

    def path(self, **kwargs) -> str:
        return "orders"
