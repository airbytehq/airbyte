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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
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
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
    Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        self.logger.info(f"Cursor Field is = {self.cursor_field}")
        return response.json().get("data")

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.config.get('hospitalization_in_days'):
            return "germany/history/hospitalization/"+str(self.config.get('hospitalization_in_days'))
        return "germany/history/hospitalization/"


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
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        return [
            Germany(),
            GermanyAgeGroups(),
            GermanyHistoryCases(config=config),
            GermanHistoryIncidence(config=config),
            GermanHistoryDeaths(config=config),
            GermanHistoryRecovered(config=config),
            GermanHistoryFrozenIncidence(config=config),
            GermanHistoryHospitalization(config=config)
            ]
