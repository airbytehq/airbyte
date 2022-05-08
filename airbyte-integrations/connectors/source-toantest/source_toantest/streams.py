from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from requests.auth import AuthBase
from requests import models
from typing import Mapping,List,Optional,Any,MutableMapping,Iterable
import requests
from datetime import datetime,timedelta,timezone

class ToantestAuthenticator(AuthBase):
    
    SYMBOLS = "VND,USD"

    def __init__(self,access_key) -> None:
        super().__init__()
        self._access_key = access_key

    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        params = {
            "access_key": self._access_key
            ,"symbols": self.SYMBOLS
        }
        r.prepare_url(r.url,params)
        return r

class ToantestStream(HttpStream):

    url_base = "http://api.exchangeratesapi.io/v1/"
    primary_key = None
    

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()

class Latest(ToantestStream):

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return "latest"

class ToantestStreamIncremental(ToantestStream,IncrementalMixin):

    cursor_field = "date"
    
    def __init__(self, start_date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date: str = start_date
        self._cursor_value = None

    @property
    def state(self):
        if self._cursor_value:
            # return {self.cursor_field:self._cursor_value}
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d')}
        else:
            # return {self.cursor_field:self.start_date}
            return {self.cursor_field: self.start_date.strftime('%Y-%m-%d')}

    @state.setter
    def state(self,source_state):
        # self._cursor_value = source_state[self.cursor_field]
        self._cursor_value = datetime.strptime(source_state[self.cursor_field], '%Y-%m-%d')

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if not self._cursor_value:
            self._cursor_value = datetime(1990,1,1)
        latest_record_date = datetime.strptime(latest_record[self.cursor_field], '%Y-%m-%d')
        self._cursor_value = max(self._cursor_value, latest_record_date)
        return {}

    # def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
    #     for record in super().read_records(*args, **kwargs):
    #         if not self._cursor_value:
    #             self._cursor_value = datetime(1990,1,1)
    #         latest_record_date = datetime.strptime(record[self.cursor_field], '%Y-%m-%d')
    #         self._cursor_value = max(self._cursor_value, latest_record_date)

    #         yield record

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now():
            dates.append({self.cursor_field: start_date.strftime('%Y-%m-%d')})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%d') if stream_state and self.cursor_field in stream_state else self.start_date
        return self._chunk_date_range(start_date)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return stream_slice['date']

class Historical(ToantestStreamIncremental):

    pass