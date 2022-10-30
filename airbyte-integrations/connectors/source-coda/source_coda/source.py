#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from requests.auth import AuthBase

BASE_URL = "https://coda.io/apis/v1/"

# Basic full refresh stream
class CodaStream(HttpStream, ABC):
   

    url_base = BASE_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()['items']


"""
    Source stream paths defined in coda
"""

class UserDetails(CodaStream):

    primary_key = "USER_DETAILS"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "whoami"


class Docs(CodaStream):

    primary_key = "DOCS"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "docs"


class Permissions(CodaStream):

    primary_key = "PERMISSIONS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/acl/permissions"



class Categories(CodaStream):

    primary_key = "CATEGORIES"


    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "categories"




class Pages(CodaStream):

    primary_key = "PAGES"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/pages"

class Tables(CodaStream):

    primary_key = "TABLES"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/tables"



class Columns(CodaStream):

    primary_key = "COLUMNS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/columns"


class Formulas(CodaStream):

    primary_key = "FORMULAS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/formulas"

class Controls(CodaStream):

    primary_key = "CONTROLS"

    def __init__(self, doc_id, **kwargs):
        super().__init__(**kwargs)
        self._doc_id = doc_id

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"docs/{self._doc_id}/controls"







# Basic incremental stream
class IncrementalCodaStream(CodaStream, ABC):
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


class Employees(IncrementalCodaStream):
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
class SourceCoda(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            token = config.get("auth_token")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}whoami",headers=headers)
            user_details_stream = UserDetails(authenticator=TokenAuthenticator(token=config.get("auth_token")))
            next(user_details_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e



    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        stream_args = {
            "authenticator": TokenAuthenticator(token=config.get("auth_token")),
        }

        additional_args = {
            **stream_args,
            'doc_id': config.get('doc_id')
        }

        return [
            UserDetails(**stream_args),
            Docs(**stream_args),
            Permissions(**additional_args),
            Categories(**stream_args),
            Pages(**additional_args),
            Tables(**additional_args),
            # Columns(**additional_args),
            # Rows(authenticator=auth, **config),
            Formulas(**additional_args),
            Controls(**additional_args),
            # Account(authenticator=auth, **config),
            # Analytics(authenticator=auth, **config),
        ]
