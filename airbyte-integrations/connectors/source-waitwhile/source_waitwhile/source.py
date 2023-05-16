from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from urllib.parse import urlparse
from urllib.parse import parse_qs


class WaitwhileStream(HttpStream, ABC):
    url_base = "https://api.waitwhile.com/v2/"
    primary_key = "id"
    limit = 100

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(authenticator=TokenAuthenticator(config.get("apikey")), **kwargs)
        self.start_date = config.get("start_date")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        end_at = response.json().get("endAt")

        if end_at:
            return {"startAfter": end_at}

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "desc": False}
        if next_page_token:
            params.update(**next_page_token)

        return params

    def adapt_datetatime_fields(self, records):
        dt_fields = ["completedTime", "serveTime", "bookingTime", "lastVisit",
                     "waitlistTime", "created", "updated", "removedTime", "cancelTime"]
        new_records = []
        for rec in records:
            for key in dt_fields:
                if key in rec:
                    if rec[key]:
                        rec[key] = rec[key].replace("Z", "")
            new_records.append(rec)
        return new_records

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        print(response.url)
        yield from self.adapt_datetatime_fields(response.json().get("results", []))


class IncrementalWaitwhileStream(WaitwhileStream, ABC):
    state_checkpoint_interval = WaitwhileStream.limit

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, **kwargs)
        self.use_lookback = False
        self.lookback_window = config.get("lookback_window", -1)
        self.delta_from_start = config.get("delta_from_start", -1)

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if self.use_lookback:
            start = pendulum.today().subtract(days=self.lookback_window)
            params.update({"fromBookingDate": str(start)[:16]})
            if self.delta_from_start >= 0:
                params.update({"toBookingDate": str(
                    start.add(days=self.delta_from_start+1))[:16]})
        else:
            last_stream_state = stream_state.get(self.cursor_field)
            if last_stream_state:
                params.update({"fromTime": pendulum.parse(last_stream_state)})
            else:
                params.update({"fromTime": pendulum.parse(self.start_date)})
        return params

    @property
    def cursor_field(self) -> str:
        """x
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "updated"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        current_state_value = current_stream_state.get(
            self.cursor_field, self.start_date)
        last_record_value = latest_record.get(
            self.cursor_field, self.start_date)
        return {self.cursor_field: max(current_state_value, last_record_value)} if not self.use_lookback else current_stream_state


class Locations(WaitwhileStream):
    """
    List locations data source.
    """

    @property
    def use_cache(self) -> bool:
        return True

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "locations"


class Services(WaitwhileStream):
    """
    List services data source.
    """

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "services"


class Resources(WaitwhileStream):
    """
    List resources data source.
    """

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "resources"


class Users(WaitwhileStream):
    """
    List users data source.
    """

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "users"


class LocationStatus(WaitwhileStream):
    """
    List location status data source.
    """

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "location-status"


class Visits(IncrementalWaitwhileStream):
    """
    List location status data source.
    If lookback window is set to >=0, then the stream will use the lookback window to get the data and incremental behavior will be ignored.
    The main difference is that fromBookingDate, which looks at 'date' field, is used instead of fromTime, which looks at 'updated' field.
    """

    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, **kwargs)
        self.use_lookback = config.get("lookback_window", -1) >= 0

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "visits"


class Customers(IncrementalWaitwhileStream):
    """
    List location status data source.
    """

    cursor_field = "updated"
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "customers"


class LocationsAvailability(HttpSubStream):
    """
    List locations availability data source.
    """

    url_base = "https://api.waitwhile.com/v2/"
    step_size = 10

    primary_key = None

    def __init__(self, parent: Locations, config: Mapping[str, Any], **kwargs):
        super().__init__(parent=parent, authenticator=TokenAuthenticator(
            config.get("apikey")), **kwargs)
        self.location_id = None
        self.start_date = pendulum.parse(config.get("start_date"))
        self.n_days_availability_horizon = config.get(
            "n_days_availability_horizon", 0)
        self.n_days_availability_lookback = config.get(
            "n_days_availabilty_lookback", 0)
        self.use_start_date = config.get("use_start_date_availability", False)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "visits/availability"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"locationId": self.location_id,
                  "fromDate": stream_slice["from"], "toDate": stream_slice["to"]}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        response_json = response.json()
        response_json = [dict(x, **{"locationId": self.location_id})
                         for x in response_json]
        print(response.url)
        if response_json:
            yield from response_json
        return []

    def get_start_date(self) -> pendulum.DateTime:
        """
        Get start date for stream based on stream_state. If date is not in stream stade, then the start date from the config is used.
        Args:
            stream_state (Mapping[str, Any], optional): Stream state. Defaults to None.

        Returns:
            pendulum.DateTime: start date.
        """
        print("lookback", self.n_days_availability_lookback)
        return pendulum.today().subtract(days=self.n_days_availability_lookback) if not self.use_start_date else self.start_date

    def get_stop_date(self) -> pendulum.DateTime:
        """
        Get stop date for stream based on n_days_availability_horizon.
        Returns:
            pendulum.DateTime: DateTime object representing the stop date.
        """
        return pendulum.today().add(days=self.n_days_availability_horizon+1)

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """_summary_

        Args:
            sync_mode (SyncMode): sync mode for the stream
            cursor_field (List[str], optional): Cursor field for stream. Defaults to None.
            stream_state (Mapping[str, Any], optional): State for stream. Defaults to None.

        Returns/Yields:
            Iterable[Optional[Mapping[str, Any]]]: Slices (dict with location id, from and to dates) for slice.
        """
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                self.location_id = record["id"]
                print("Location", self.location_id)
                for start, end in self.chunk_dates():
                    print(start, "-", end)
                    yield {"parent": record, "from": start, "to": end}

    def chunk_dates(self) -> Iterable[Tuple[str, str]]:
        stop = self.get_stop_date()
        after = self.get_start_date()
        while after < stop:
            before = min(stop, after.add(days=self.step_size))
            yield str(after)[:16], str(before)[:16]
            after = before.add(minutes=0)


class SourceWaitwhile(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            headers = dict(Accept="application/json", apikey=config["apikey"])
            url = "https://api.waitwhile.com/v2/"
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        locations = Locations(config=config)
        return [
            locations,
            Services(config=config),
            Resources(config=config),
            Users(config=config),
            LocationStatus(config=config),
            Customers(config=config),
            Visits(config=config),
            LocationsAvailability(
                parent=locations,
                config=config
            ),
        ]
