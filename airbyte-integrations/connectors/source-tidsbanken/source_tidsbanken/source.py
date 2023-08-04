#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode


# Basic full refresh stream
class TidsbankenStream(HttpStream, ABC):

    url_base = "http://api.tidsbanken.net/dev/"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {"key": self.config.get("api_key")}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        print('Rows:', len(response.json()))

        yield from response.json()


class Avdelinger(TidsbankenStream):

    primary_key = "AvdelingID"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "avdelinger/finn"


class Omsetning(TidsbankenStream):

    primary_key = "InntekstplanId"

    # TODO: this need incremental logic based on Date somehow

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "omsetning/finn"


class Lonn(TidsbankenStream):

    primary_key = "TimeregistreringID"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "lonn/finn"


class IncrementalTidsbankenStream(TidsbankenStream, ABC):

    state_checkpoint_interval = 100

    @property
    def cursor_field(self) -> str:

        return "EndretDato"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if stream_state:
            state_start_date = pendulum.parse(
                stream_state.get(self.cursor_field))

        else:
            state_start_date = pendulum.parse(
                self.config.get("start_date"))

        start_date = state_start_date.start_of("day")
        end_date = pendulum.now("UTC").start_of("day")
        slices = []
        current_date = start_date
        while current_date < end_date:

            slices.append(
                {
                    self.cursor_field: current_date,
                }
            )
            next_date = current_date.add(days=self.config["slice_interval"])
            current_date = next_date

        return slices

    def request_params(self, stream_slice: Mapping[str, Any], stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any]) -> MutableMapping[str, Any]:
        start_time = stream_slice[self.cursor_field]
        end_time = start_time.add(days=self.config["slice_interval"])

        start_time = start_time.to_iso8601_string()[0:10]
        end_time = end_time.to_iso8601_string()[0:10]
        print('Slice : ', start_time, '-', end_time)

        filter_param = f"{self.cursor_field} gt datetime('{start_time}') and {self.cursor_field} lt datetime('{end_time}') "
        print('State : ', stream_state)
        return {
            "key": self.config["api_key"],
            "$filter": filter_param,
            "$orderby": f"{self.cursor_field} asc"
        }

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:

        current_stream_cursor_value = current_stream_state.get(
            self.cursor_field, self.config.get("start_date"))
        latest_record_cursor_value = latest_record[self.cursor_field]
        latest_cursor = max(pendulum.parse(
            latest_record_cursor_value), pendulum.parse(current_stream_cursor_value))

        return {self.cursor_field: latest_cursor.isoformat()}


class Ansatte(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "Ansattnummer"

    def path(self, **kwargs) -> str:

        return "ansatte/finn"


class Timelister(IncrementalTidsbankenStream):

    cursor_field = "EndretDato"

    # Primary key. Required
    primary_key = "TimeregistreringID"

    def path(self, **kwargs) -> str:

        return "timelister/finn"


class Vakter(IncrementalTidsbankenStream):

    cursor_field = "EndretDato"

    # Primary key. Required
    primary_key = "PlanID"

    def path(self, **kwargs) -> str:

        return "plan/finn"


class Arter(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "arter/finn"


class Arbeidstyper(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "arbeidstyper/finn"


class Aktiviteter(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "aktiviteter/finn"


class Eksporter(IncrementalTidsbankenStream):

    cursor_field = "EndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "eksporter/finn"


class Plan(IncrementalTidsbankenStream):

    cursor_field = "EndretDato"

    # Primary key. Required
    primary_key = "PlanID"

    def path(self, **kwargs) -> str:

        return "plan/finn"


class Prosjekter(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "prosjekter/finn"


class Prosjektlinjer(IncrementalTidsbankenStream):

    cursor_field = "SistEndretDato"

    # Primary key. Required
    primary_key = "id"

    def path(self, **kwargs) -> str:

        return "prosjektlinjer/finn"


class SourceTidsbanken(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        stream = Avdelinger(config)
        try:
            next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        return [Omsetning(config), Avdelinger(config), Ansatte(config), Timelister(config), Vakter(config), Arbeidstyper(config), Arter(config), Aktiviteter(config), Prosjekter(config), Eksporter(config), Lonn(config), Plan(config), Prosjektlinjer(config)]
