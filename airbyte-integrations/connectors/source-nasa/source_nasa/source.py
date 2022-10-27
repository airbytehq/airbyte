#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime, time, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream

date_format = "%Y-%m-%d"


class NasaStream(HttpStream, ABC):

    api_key = "api_key"
    url_base = "https://api.nasa.gov/"

    def __init__(self, config: Mapping[str, any], **kwargs):
        super().__init__()
        self.config = config

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {self.api_key: self.config[self.api_key]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        r = response.json()
        if type(r) is dict:
            yield r
        else:  # We got a list
            yield from r


class NasaApod(NasaStream, IncrementalMixin):

    cursor_field = "date"
    primary_key = "date"
    start_date_key = "start_date"
    end_date_key = "end_date"

    def __init__(self, config: Mapping[str, any], **kwargs):
        super().__init__(config)
        self.start_date = (
            datetime.strptime(config.pop(self.start_date_key), date_format) if self.start_date_key in config else datetime.now()
        )
        self.end_date = datetime.strptime(config.pop(self.end_date_key), date_format) if self.end_date_key in config else datetime.now()
        self.sync_mode = SyncMode.full_refresh
        self._cursor_value = self.start_date

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: self._cursor_value.strftime(date_format)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], date_format)

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and end date.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date <= self.end_date:
            dates.append({self.cursor_field: start_date.strftime(date_format)})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if (
            stream_state
            and self.cursor_field in stream_state
            and datetime.strptime(stream_state[self.cursor_field], date_format) > self.end_date
        ):
            return []
        if sync_mode == SyncMode.full_refresh:
            return [self.start_date]

        start_date = (
            datetime.strptime(stream_state[self.cursor_field], date_format)
            if stream_state and self.cursor_field in stream_state
            else self.start_date
        )
        return self._chunk_date_range(start_date)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "planetary/apod"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        request_dict = {**self.config, **super().request_params(stream_state, stream_slice, next_page_token)}
        if self.sync_mode == SyncMode.full_refresh:
            request_dict[self.start_date_key] = self.start_date.strftime(date_format)
            request_dict[self.end_date_key] = self.end_date.strftime(date_format)
        else:
            request_dict[self.primary_key] = stream_slice[self.cursor_field]
        return request_dict

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        self.sync_mode = kwargs.get("sync_mode", SyncMode.full_refresh)
        if self._cursor_value and self._cursor_value > self.end_date:
            yield []
        else:
            for record in super().read_records(*args, **kwargs):
                if self._cursor_value:
                    latest_record_date = datetime.strptime(record[self.cursor_field], date_format)
                    self._cursor_value = max(self._cursor_value, latest_record_date)
                yield record


# Source
class SourceNasa(AbstractSource):

    count_key = "count"
    start_date_key = "start_date"
    end_date_key = "end_date"
    min_count_value, max_count_value = 1, 101
    min_date = datetime.strptime("1995-06-16", date_format)
    max_date = datetime.combine(datetime.today(), time(0, 0)) + timedelta(days=1)
    invalid_conbination_message_template = "Invalid parameter combination. Cannot use {} and {} together."
    invalid_parameter_value_template = "Invalid {} value: {}. {}."
    invalid_parameter_value_range_template = "The value should be in the range [{},{})"

    def _parse_date(self, date_str: str) -> Union[datetime, str]:
        """
        Parses the date string into a datetime object.

        :param date_str: string containing the date according to DATE_FORMAT
        :return Union[datetime, str]: str if not correctly formatted or if it does not satify the constraints [self.MIN_DATE, self.MAX_DATE), datetime otherwise.
        """
        try:
            date = datetime.strptime(date_str, date_format)
            if date < self.min_date or date >= self.max_date:
                return self.invalid_parameter_value_template.format(
                    self.date_key, date_str, self.invalid_parameter_value_range_template.format(self.min_date, self.max_date)
                )
            else:
                return date
        except ValueError:
            return self.invalid_parameter_value_template.format(self.date_key, date_str, f"It should be formatted as '{date_format}'")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Verifies that the input configuration supplied by the user can be used to connect to the underlying data source.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        if self.start_date_key in config:
            start_date = self._parse_date(config[self.start_date_key])
            if type(start_date) is not datetime:
                return False, start_date

            if self.count_key in config:
                return False, self.invalid_conbination_message_template.format(self.start_date_key, self.count_key)

        if self.end_date_key in config:
            end_date = self._parse_date(config[self.end_date_key])
            if type(end_date) is not datetime:
                return False, end_date

            if self.count_key in config:
                return False, self.invalid_conbination_message_template.format(self.end_date_key, self.count_key)

            if self.start_date_key not in config:
                return False, f"Cannot use {self.end_date_key} without specifying {self.start_date_key}."

            if start_date > end_date:
                return False, f"Invalid values. start_date ({start_date}) needs to be lower than or equal to end_date ({end_date})."

        if self.count_key in config:
            count_value = config[self.count_key]
            if count_value < self.min_count_value or count_value >= self.max_count_value:
                return False, self.invalid_parameter_value_template.format(
                    self.count_key,
                    count_value,
                    self.invalid_parameter_value_range_template.format(self.min_count_value, self.max_count_value),
                )

        try:
            stream = NasaApod(authenticator=None, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [NasaApod(authenticator=None, config=config)]
