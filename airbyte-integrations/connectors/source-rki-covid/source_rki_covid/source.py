#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json().get("data")

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
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/cases/" + str(self.date_to_int(self.start_date))
        return "germany/history/cases/"


# source: germany/history/incidence/:days | Incremental
class GermanHistoryIncidence(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/incidence/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/incidence/" + str(self.date_to_int(self.start_date))
        return "germany/history/incidence/"


# source: germany/history/deaths/:days | Incremental
class GermanHistoryDeaths(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/deaths/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/deaths/" + str(self.date_to_int(self.start_date))
        return "germany/history/deaths/"


# source: germany/history/recovered/:days | Incremental
class GermanHistoryRecovered(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/recovered/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/recovered/" + str(self.date_to_int(self.start_date))
        return "germany/history/recovered/"


# source: germany/history/frozen-incidence/:days | Incremental
class GermanHistoryFrozenIncidence(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/frozen-incidence/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data").get("history")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/frozen-incidence/" + str(self.date_to_int(self.start_date))
        return "germany/history/frozen-incidence/"


# source: germany/history/hospitalization/:days | Incremental
class GermanHistoryHospitalization(IncrementalRkiCovidStream):
    """Docs: https://api.corona-zahlen.org/germany/germany/history/hospitalization/:days"""

    primary_key = None

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.start_date = config.get("start_date")

    @property
    def source_defined_cursor(self) -> bool:
        return False

    @property
    def cursor_field(self) -> str:
        return "date"

    def date_to_int(self, start_date) -> int:
        diff = datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")
        if diff.days <= 0:
            return 1
        return diff.days

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(stream_state=stream_state, **kwargs)
        if stream_state:
            for record in records:
                if record[self.cursor_field] > stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.json().get("data"):
            return response.json().get("data")
        return [{}]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.start_date:
            return "germany/history/hospitalization/" + str(self.date_to_int(self.start_date))
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
            req = requests.get(RkiCovidStream.url_base + "germany")
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
            GermanHistoryHospitalization(config=config),
        ]
