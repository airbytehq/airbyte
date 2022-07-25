#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from requests.auth import AuthBase


class FlexportError(Exception):
    pass


class FlexportStream(HttpStream, ABC):
    url_base = "https://api.flexport.com/"
    raise_on_http_errors = False
    primary_key = "id"
    page_size = 100

    def __init__(self, authenticator: Union[AuthBase, HttpAuthenticator] = None, start_date: str = None):
        super().__init__(authenticator=authenticator)

        self._authenticator = authenticator
        self.start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # https://apidocs.flexport.com/v3/tag/Pagination/
        # All list endpoints return paginated responses. The response object contains
        # elements of the current page, and links to the previous and next pages.
        data = response.json()["data"]
        next = data.get("next")

        if next:
            url = urlparse(next)
            qs = dict(parse_qsl(url.query))

            return {
                "page": qs["page"],
                "per": qs["per"],
            }

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        if next_page_token:
            return next_page_token

        return {
            "page": 1,
            "per": self.page_size,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # https://apidocs.flexport.com/v3/tag/Response-Semantics
        json = response.json()

        http_error = None
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            http_error = exc

        flexport_error = None
        try:
            flexport_error = json.get("error")
        except AttributeError:
            raise FlexportError("Unexpected response") from http_error

        if flexport_error:
            try:
                if "code" in flexport_error and "message" in flexport_error:
                    raise FlexportError(f"{flexport_error['code']}: {flexport_error['message']}") from http_error
            except TypeError:
                pass

            raise FlexportError(f"Unexpected error: {flexport_error}") from http_error

        if http_error:
            raise http_error

        yield from json["data"]["data"]


class IncrementalFlexportStream(FlexportStream, ABC):
    epoch_start = pendulum.from_timestamp(0, tz="UTC").to_iso8601_string()

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current = current_stream_state.get(self.cursor_field, self.epoch_start)
        latest = latest_record.get(self.cursor_field, self.epoch_start)

        return {
            self.cursor_field: max(latest, current),
        }

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if not stream_state:
            stream_state = {}

        from_date = pendulum.parse(stream_state.get(self.cursor_field, self.start_date))
        end_date = max(from_date, pendulum.tomorrow("UTC"))

        date_diff = end_date - from_date
        if date_diff.years > 0:
            interval = pendulum.duration(months=1)
        elif date_diff.months > 0:
            interval = pendulum.duration(weeks=1)
        elif date_diff.weeks > 0:
            interval = pendulum.duration(days=1)
        else:
            interval = pendulum.duration(hours=1)

        while True:
            to_date = min(from_date + interval, end_date)
            yield {"from": from_date.isoformat(), "to": to_date.add(seconds=1).isoformat()}
            from_date = to_date
            if from_date >= end_date:
                break


class Companies(FlexportStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "network/companies"


class Locations(FlexportStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "network/locations"


class Products(FlexportStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "products"


class Invoices(FlexportStream):
    page_size = 100

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoices"


class Shipments(IncrementalFlexportStream):
    cursor_field = "updated_at"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "shipments"

    def request_params(self, stream_slice: Mapping[str, any] = None, **kwargs) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_slice=stream_slice, **kwargs),
            "sort": self.cursor_field,
            "direction": "asc",
            "f.updated_at.gt": stream_slice["from"],
            "f.updated_at.lt": stream_slice["to"],
        }
