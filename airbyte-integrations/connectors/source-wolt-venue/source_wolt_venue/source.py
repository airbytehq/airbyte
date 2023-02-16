#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Iterator

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class WoltVenueStream(HttpStream, ABC):
    primary_key = None
    state_checkpoint_interval = 1

    def __init__(self, config: Mapping[str, Any], venues_mapping: Iterator[Tuple[str, str]], **kwargs):
        super().__init__()
        self.refresh_token = config.get("refresh_token")
        self.start_date = config.get("start_date")
        self.stop_date = pendulum.now().format("YYYY-MM-DDTHH:00:00")
        self.access_token = None
        self.update_access_token()

        self.venues_mapping = venues_mapping
        self.venue_code, self.venue_name = next(self.venues_mapping)

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return "end_time"

    def update_access_token(self):
        form_data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        url = "https://authentication.wolt.com/v1/wauth2/access_token"
        response = requests.post(url, data=form_data, verify=False)
        self.access_token = response.json().get("access_token")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """

        data = response.json()
        max_resp_end_time = max([x['end_time'] for x in data])
        if max_resp_end_time < self.stop_date:
            return {"end_time": max_resp_end_time}
        else:
            self.venue_code, self.venue_name = next(self.venues_mapping, (None, None))

        if self.venue_code:
            return {"code_": self.venue_code}
        return {}

    @property
    def url_base(self) -> str:
        return f"https://restaurant-api.wolt.com/v1/merchant-admin/venues/{self.venue_code}/"

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        max_resp_end_time = next_page_token.get('end_time', self.start_date) if next_page_token else self.start_date
        start_time = stream_state.get(self.venue_code, max_resp_end_time)
        # start_time - 10 hours to avoid missing data
        start_time = pendulum.parse(start_time).subtract(hours=10).format("YYYY-MM-DDTHH:00:00")

        end_ts = pendulum.parse(start_time).add(days=7).format("YYYY-MM-DDTHH:00:00")
        end_time = min(str(end_ts), str(self.stop_date))



        params = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": "P0DT1H",
        }
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        data = sorted(data, key=lambda x: x["end_time"])
        yield from [{**x, **{"venue": self.venue_name}} for x in data]

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """

        current_stream_value = current_stream_state.get(self.venue_code, self.start_date)
        latest_record_value = latest_record.get(self.cursor_field, self.start_date)
        new_value = max(current_stream_value, latest_record_value)
        new_state = {self.venue_code: new_value}

        new_stream_state = {**current_stream_state, **new_state}
        return new_stream_state


class OfflineMinutes(WoltVenueStream):
    cursor_field = "end_time"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        To define the path of the stream.
        """
        return "offline-minutes"


class SourceWoltVenue(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        venues_mapping = [
            ("5e8c54125fb96f4417ebc836", "B62"),
            ("620ba315e563c1faa7a9b2d6", "T18"),
            ("620ba4e460f7329be919d9c1", "TMG"),
            ("620ba7cde15dc14dbd1e5dbc", "Storo"),
        ]
        return [OfflineMinutes(config=config, venues_mapping=iter(venues_mapping))]
