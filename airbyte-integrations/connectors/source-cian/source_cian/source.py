from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode


class CianStream(HttpStream, ABC):
    url_base = "https://public-api.cian.ru/"
    date_format: str = "%Y-%m-%d"

    def __init__(self, authenticator: TokenAuthenticator):
        super().__init__(authenticator)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class BuilderCalls(CianStream):
    primary_key = "id"

    def __init__(self, authenticator: TokenAuthenticator, start_date: str, end_date: str, building_id: Optional[int] = None):
        super().__init__(authenticator)
        self.start_date: datetime.date = datetime.strptime(start_date, self.date_format).date()
        self.end_date: datetime.date = datetime.strptime(end_date, self.date_format).date()
        self.building_id: str | None = building_id

    def path(self, *args, **kwargs) -> str:
        return "v1/get-builder-calls/"

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """One slice for each request -> each day"""
        for t_delta in range((self.end_date - self.start_date).days):
            dt: datetime = datetime(year=self.start_date.year, month=self.start_date.month, day=self.start_date.day) + timedelta(days=t_delta)
            yield {"load_date": dt.isoformat()}

    def request_params(self, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        data: dict[str, any] = {
            "onDate": stream_slice["load_date"]
        }
        if self.building_id is not None:
            data["newbuildingId"] = self.building_id
        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json: dict[str, any] = response.json()
        status: int = response.status_code
        if status in [400, 401, 429, 500]:
            error_text: str = response_json["result"]["message"]
            self.logger.info(f"Request failed with status {status}: {error_text}")
            yield from []
        else:
            yield from response_json["result"]["calls"]


class SourceCian(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["building_id"] = config.get("building_id", None)
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth = TokenAuthenticator(token=config["token"])
        return [BuilderCalls(
            authenticator=auth,
            start_date=config["start_date"],
            end_date=config["end_date"],
            building_id=config["building_id"]
        )]
