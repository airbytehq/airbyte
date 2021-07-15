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


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.models import SyncMode
import requests
import pytz
from datetime import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from urllib.parse import parse_qsl, urlparse

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

DATATIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Basic full refresh stream
class SourceZendeskSupportStream(HttpStream, ABC):
    """"Basic Zendesk class"""

    def __init__(self, subdomain: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subdomain = subdomain

    @property
    def url_base(self) -> str:
        return f"https://{self.subdomain}.zendesk.com/api/v2/"


class UserSettingsStream(SourceZendeskSupportStream):
    """Stream for checking of a request token"""

    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return 'account/settings.json'

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API as is"""
        yield from [response.json().get('settings') or {}]

    def get_settings(self):
        for resp in self.read_records(SyncMode.full_refresh):
            return resp, None
        return None, "not found settings"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class BasicListStream(SourceZendeskSupportStream, ABC):
    """Base class for all data lists with increantal stream"""
    # max size of one data chunk. 100 is limitation of ZenDesk
    state_checkpoint_interval = 100
    primary_key = "id"

    def __init__(self, start_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = start_date

    def _prepare_query(self,
                       type: str,
                       updated_after: datetime = None):
        conds = [f'type:{type}']
        conds.append(
            'created>%s' % datetime.strftime(
                self.start_date.replace(tzinfo=pytz.UTC),
                DATATIME_FORMAT
            )
        )
        if updated_after:
            conds.append(
                'updated>%s' % datetime.strftime(
                    updated_after.replace(tzinfo=pytz.UTC),
                    DATATIME_FORMAT
                )
            )
        return {
            'query': ' '.join(conds)
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json()['next_page']
        # TODO test page
        # next_page = """https://foo.zendesk.com/api/v2/search.json?query=\"type:Group hello\"\u0026sort_by=created_at\u0026sort_order=desc\u0026page=2"""
        if next_page:
            next_page = dict(parse_qsl(urlparse(next_page).query)).get('page')
            if next_page:
                return {'next_page': next_page}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API AS IS"""
        yield from response.json()['results'] or []


class Users(BasicListStream):
    primary_key = 'id'
    entity_type = 'user'
    cursor_field = 'updated_at'

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return 'search.json'

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        updated_after = None
        if stream_state and stream_state.get(self.cursor_field):
            updated_after = datetime.strptime(stream_state[self.cursor_field],DATATIME_FORMAT)

        res = self._prepare_query('user', updated_after)
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
        return {
            self.cursor_field: max(
                (latest_record or {}).get(self.cursor_field, ""),
                (current_stream_state or{}).get(self.cursor_field, "")
            )
        }



# # Basic incremental stream
# class IncrementalSourceZendeskSupportStream(SourceZendeskSupportStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}


# class Employees(IncrementalSourceZendeskSupportStream):
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

    # def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
    #     """
    #     TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

    #     This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
    #     to most other methods in this class to help you form headers, request bodies, query params, etc..

    #     For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
    #     'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
    #     The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

    #     :param response: the most recent response from the API
    #     :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
    #             If there are no more pages in the result, return None.
    #     """
    #     return None

    # def request_params(
    #     self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    # ) -> MutableMapping[str, Any]:
    #     """
    #     TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
    #     Usually contains common params e.g. pagination size etc.
    #     """
    #     return {}

    # def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
    #     """
    #     TODO: Override this method to define how a response is parsed.
    #     :return an iterable containing each record in the response
    #     """
    #     yield {}
