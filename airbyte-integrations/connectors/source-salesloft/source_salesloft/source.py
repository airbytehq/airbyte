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


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class SalesloftStream(HttpStream, ABC):

    # TODO: Fill in the url base. Required.
    url_base = "https://api.salesloft.com/v2/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json()['metadata']['paging'].get('next_page')
        return None if not next_page else {'page': next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token and 'page' in next_page_token:
            return {'per_page': 100, 'page': next_page_token['page']}

        return {'per_page': 100, 'page': 1}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get('data')
        if not data:
            yield {}
            return
        for element in data:
            yield element


class Users(SalesloftStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = 'id'

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return 'users.json'


# Basic incremental stream
class IncrementalSalesloftStream(SalesloftStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class Employees(IncrementalSalesloftStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")


# Source
class SourceSalesloft(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            api_key = config['api_key']
            response = requests.get('https://api.salesloft.com/v2/me.json', headers={'Authorization': f'Bearer {api_key}'})
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config['api_key'])  # Oauth2Authenticator is also available if you need oauth support
        return [Users(authenticator=auth)]
