#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class FreshsalesStream(HttpStream, ABC):
    url_base = "https://{}/crm/sales/api/"
    primary_key = "id"
    order_field = "updated_at"
    def __init__(self, domain_name: str, **kwargs):
        super().__init__(**kwargs)
        self.url_base = self.url_base.format(domain_name)
        self.domain_name = domain_name
        self.page = 1
        self.get_view_id()
        
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        list_result = response.json().get(self.object_name, [])
        if list_result:
            self.page += 1
            return self.page
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"page": self.page, "sort": self.order_field, "sort_type": "asc"}  
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records
    
    def get_filters(self):
        filters_url = f"https://{self.domain_name}/crm/sales/api/{self.object_name}/filters"
        auth = self.authenticator.get_auth_header()
        try:
            r = requests.get(filters_url, headers=auth)
            r.raise_for_status()
            return r.json().get('filters')
        except requests.exceptions.RequestException as e:
            return False, e

    def get_view_id(self):
        if hasattr(self, "filter_name"):
            filters = self.get_filters()
            return next(filter['id'] for filter in filters if filter['name'] == self.filter_name)
        else:
            return

# Basic incremental stream
class IncrementalFreshsalesStream(FreshsalesStream, ABC):
    cursor_field = "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if stream_state:
            params[self.filter_field] = stream_state.get(self.cursor_field)

    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record.get(self.cursor_field) >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class Contacts(IncrementalFreshsalesStream):
    object_name = "contacts"
    filter_name = "All Contacts"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        view_id = self.get_view_id()
        return f"{self.object_name}/view/{view_id}"



# class Employees(IncrementalFreshsalesStream):
#     """
#     TODO: Change class name to match the table/data source this stream corresponds to.
#     """

#     # TODO: Fill in the cursor_field. Required.
#     cursor_field = "start_date"

#     # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
#     primary_key = "employee_id"

#     def path(self, **kwargs) -> str:
#         """
#         TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
#         return "single". Required.
#         """
#         return "employees"

#     def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
#         """
#         TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

#         Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
#         This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
#         section of the docs for more information.

#         The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
#         necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
#         This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

#         An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
#         craft that specific request.

#         For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
#         this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
#         till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
#         the date query param.
#         """
#         raise NotImplementedError("Implement stream slices or delete this method!")

class FreshsalesAuthenticator(TokenAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Token token={self._token}"}

# Source
class SourceFreshsales(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = FreshsalesAuthenticator(token=config["api_key"]).get_auth_header()
        url = f'https://{config["domain_name"]}/crm/sales/api/contacts/filters'
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = FreshsalesAuthenticator(token=config["api_key"])
        args = {"authenticator": auth, "domain_name": config["domain_name"]}
        return [Contacts(**args)]
