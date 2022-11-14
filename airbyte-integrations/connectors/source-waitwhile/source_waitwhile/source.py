from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class WaitwhileStreamAvailability(HttpStream, ABC):
    url_base = "https://api.waitwhile.com/v2/"

    primary_key = None

    def __init__(self, start_date: str, location_ids: Optional[Iterable[str]], n_days_availability_horizon: str, **kwargs):
        super().__init__(**kwargs)
        self.location_ids = location_ids
        self.location_id = next(self.location_ids)
        self.start_date = pendulum.parse(start_date)
        self.stop_date = pendulum.today().add(days=n_days_availability_horizon)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        params = {}

        resp_records = response.json()
        last_date = None

        if len(resp_records) == 0:
            self.location_id = next(self.location_ids, None)
        else:
            last_date = pendulum.parse(resp_records[-1].get("date")).add(minutes=1)
            if last_date >= self.stop_date:
                self.location_id = next(self.location_ids, None)
                last_date = None

        if self.location_id:
            params["locationId"] = self.location_id
            if last_date:
                params["fromDate"] = str(last_date)[:16]
            return params

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"locationId": self.location_id}
        if next_page_token:
            params.update(**next_page_token)

        if "fromDate" in params:
            return params

        stream_start_date = str(self.start_date)[:16]
        last_stream_date = stream_state.get("date", {}).get(self.location_id, stream_start_date)
        params["fromDate"] = str(last_stream_date)[:16] if last_stream_date else stream_start_date
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        if response.status_code != 200:
            return []

        response_json = response.json()
        response_json = [dict(x, **{"locationId": self.location_id}) for x in response_json]
        if response_json:
            yield from response_json

        return []


class IncrementalWaitwhileStreamAvailability(WaitwhileStreamAvailability, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """

        state_mapping = current_stream_state.get(self.cursor_field, {})
        if state_mapping:
            state_value = state_mapping.get(self.location_id, self.start_date)
        else:
            state_mapping = {}
            state_value = self.start_date

        last_record_value = latest_record.get(self.cursor_field)
        if last_record_value:
            state_mapping.update({self.location_id: last_record_value})

        return {self.cursor_field: state_mapping}


class LocationsAvailability(IncrementalWaitwhileStreamAvailability):
    """
    List locations availability data source.
    """

    cursor_field = "date"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "visits/availability"


class WaitwhileStream(HttpStream, ABC):
    url_base = "https://api.waitwhile.com/v2/"
    primary_key = None
    limit = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        end_at = response.json().get("endAt")

        if end_at:
            end_at = end_at.split(",")[-1]
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
        if response.status_code != 200:
            return []

        response_json = response.json().get("results")
        response_json = self.adapt_datetatime_fields(response_json)
        if response_json:
            yield from response_json

        return []


class WaitwhileStreamTime(HttpStream, ABC):
    url_base = "https://api.waitwhile.com/v2/"
    primary_key = None
    limit = 100

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

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

        last_stream_state = stream_state.get("updated")
        if last_stream_state:
            params.update({"fromTime": pendulum.parse(last_stream_state)})
        else:
            params.update({"fromTime": pendulum.parse(self.start_date)})

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
        if response.status_code != 200:
            return []

        response_json = response.json().get("results")
        response_json = self.adapt_datetatime_fields(response_json)
        if response_json:
            yield from response_json

        return []


class IncrementalWaitwhileStreamTime(WaitwhileStreamTime, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        """
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
        current_state_value = current_stream_state.get(self.cursor_field, self.start_date)
        last_record_value = latest_record.get(self.cursor_field)

        if last_record_value:
            return {self.cursor_field: max(current_state_value, last_record_value)}
        return {self.cursor_field: current_state_value}


class Locations(WaitwhileStream):
    """
    List locations data source.
    """

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


class Visits(IncrementalWaitwhileStreamTime):
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
        return "visits"


class Customers(IncrementalWaitwhileStreamTime):
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

    def get_location_ids(self, config):
        headers = dict(Accept="application/json", apikey=config["apikey"])
        url = "https://api.waitwhile.com/v2/locations?limit=100"
        resp = requests.get(url, headers=headers)
        location_ids = [x.get("id") for x in resp.json()["results"]]
        return iter(location_ids)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(config["apikey"])
        location_ids = self.get_location_ids(config)
        start_date = config["start_date"]
        n_days_availability_horizon = config["n_days_availability_horizon"]
        return [
            Locations(authenticator=auth),
            Services(authenticator=auth),
            Resources(authenticator=auth),
            Users(authenticator=auth),
            LocationStatus(authenticator=auth),
            Customers(authenticator=auth, start_date=start_date),
            Visits(authenticator=auth, start_date=start_date),
            LocationsAvailability(
                authenticator=auth,
                start_date=start_date,
                location_ids=location_ids,
                n_days_availability_horizon=n_days_availability_horizon
            ),
        ]
