#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from datetime import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class RkiCovidStream(HttpStream, ABC):


    url_base = "https://api.corona-zahlen.org/"

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
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield response.json()


# class that contains main source germany | full-refresh
class Germany(RkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany"""

    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "germany/"


# class that contains source age-groups in germany. | full-refresh
class GermanyAgeGroups(RkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/age-groups"""

    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "germany/age-groups"


# Basic incremental stream
class IncrementalRkiCovidStream(RkiCovidStream, ABC):

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


# source: germany/history/cases/:days | Incremental
class GermanyHistoryCases(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/cases/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._cursor_value = None

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            current_stream_state = record.get(self.cursor_field)
            # print("self._cursor_value:", self._cursor_value, "current_stream_state:", current_stream_state)
            if self._cursor_value:
                latest_state = record.get(self.cursor_field)
                self._cursor_value = max(self._cursor_value, latest_state)
            yield record
            self._cursor_value = current_stream_state
            assert self._cursor_value == current_stream_state

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('cases_in_days'):
            return "germany/history/cases/"+str(self.config.get('cases_in_days'))
        return "germany/history/cases/"


# source: germany/history/incidence/:days | Incremental
class GermanHistoryIncidence(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/incidence/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        pass

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('incidence_in_days'):
            return "germany/history/incidence/"+str(self.config.get('incidence_in_days'))
        return "germany/history/incidence/"


# source: germany/history/deaths/:days | Incremental
class GermanHistoryDeaths(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/deaths/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('deaths_in_days'):
            return "germany/history/deaths/"+str(self.config.get('deaths_in_days'))
        return "germany/history/deaths/"


# source: germany/history/recovered/:days | Incremental
class GermanHistoryRecovered(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/recovered/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('recovered_in_days'):
            return "germany/history/recovered/"+str(self.config.get('recovered_in_days'))
        return "germany/history/recovered/"


# source: germany/history/frozen-incidence/:days | Incremental
class GermanHistoryFrozenIncidence(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/frozen-incidence/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data").get("history")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('frozen_incidence_in_days'):
            return "germany/history/frozen-incidence/"+str(self.config.get('frozen_incidence_in_days'))
        return "germany/history/frozen-incidence/"


# source: germany/history/hospitalization/:days | Incremental
class GermanHistoryHospitalization(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/hospitalization/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    @property
    def cursor_field(self) -> str:
        """
        date is cursor field in the stream.
        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get("data")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('hospitalization_in_days'):
            return "germany/history/hospitalization/"+str(self.config.get('hospitalization_in_days'))
        return "germany/history/hospitalization/"


class Employees(IncrementalRkiCovidStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "date"

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
class SourceRkiCovid(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            req = requests.get(RkiCovidStream.url_base+'germany')
            if req.status_code == 200:
                return True, None
            return False, req.reason
        except Exception:
            return False, "There is a problem in source check connection."


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Defining streams to run.
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        return [
            Germany(),
            GermanyAgeGroups(),
            GermanyHistoryCases(config=config),
            # GermanHistoryIncidence(config=config),
            GermanHistoryDeaths(config=config),
            GermanHistoryRecovered(config=config),
            GermanHistoryFrozenIncidence(config=config),
            GermanHistoryHospitalization(config=config)
            ]
