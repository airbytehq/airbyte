import datetime
from abc import ABC
from typing import (
    Any,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
)

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.http import HttpSubStream

DATE_MASK = "%Y-%m-%dT%H:%M:%S.000Z"
FROM_VTEX_DATE_MASK = "%Y-%m-%dT%H:%M:%S.%f+00:00"


class VtexStream(HttpStream, ABC):
    @property
    def url_base(self) -> str:
        client_name = self._session.auth.client_name
        return f"https://{client_name}.vtexcommercestable.com.br"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(authenticator=kwargs["authenticator"])
        self.start_date = start_date

    def check_connection(self):
        start_date = datetime.datetime.now().strftime(DATE_MASK)
        orders_endpoint = "/api/oms/pvt/orders"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        params = {
            "f_creationDate": f"creationDate:[{start_date} TO {start_date}]",
            "page": 1,
        }

        url = self.url_base + orders_endpoint
        resp = requests.get(
            url, params=params, headers=headers, auth=self._session.auth
        )

        if resp.status_code != 200:
            return False, resp.content

        return True, None

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        page = response_json["paging"]["currentPage"]
        totalPages = response_json["paging"]["pages"]

        if page <= totalPages:
            return {"page": page + 1}

        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        start_date = self.start_date

        # VTEX seems to work with utc time
        end_date = (
            datetime.datetime.now() + datetime.timedelta(hours=3)
        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        if stream_state and self.cursor_field in stream_state:
            start_date = stream_state[self.cursor_field]

        page = next_page_token["page"] if next_page_token else 1

        return {
            "f_creationDate": f"creationDate:[{start_date} TO {end_date}]",
            "page": page,
        }

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield from response.json()["list"]


class IncrementalVtexStream(VtexStream, ABC):

    state_checkpoint_interval = None

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days

    @property
    def cursor_field(self) -> str:
        return "creationDate"

    def format_date_to_milliseconds(self, date_str: str) -> str:
        """
        Not sure why, VTEX answer comes with 7 digits for
        millisecond date format, here we try to make sure it stays with
        6 digits
        """

        splited_array = date_str.split("+")
        first_half = splited_array[0][:-1]
        return first_half + "+" + splited_array[1]

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest
        record with the stream's most recent state object and returning an
        updated state object.
        """
        if (
            current_stream_state is not None
            and self.cursor_field in current_stream_state
        ):
            current_date = current_stream_state[self.cursor_field]
            current_parsed_date = datetime.datetime.strptime(
                current_date, DATE_MASK
            )

            latest_record_date = latest_record.get(self.cursor_field)
            if len(latest_record_date) >= 33:
                latest_record_date = self.format_date_to_milliseconds(
                    latest_record_date
                )

            latest_record_parsed_date = datetime.datetime.strptime(
                latest_record_date, FROM_VTEX_DATE_MASK
            )

            return {
                self.cursor_field: max(
                    current_parsed_date, latest_record_parsed_date
                ).strftime(DATE_MASK)
            }
        else:
            return {self.cursor_field: self.start_date}


class VtexSubStream(HttpSubStream, IncrementalVtexStream):
    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        yield response.json()
