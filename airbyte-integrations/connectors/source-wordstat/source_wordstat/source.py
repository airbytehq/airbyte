#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_protocol.models import SyncMode
from requests.auth import AuthBase


class CookiesAuthenticator(AuthBase):

    def __init__(self, cookies: dict[str, any]):
        # TODO: simplified authenticator for MVP
        self._cookies: dict[str, any] = cookies

    def get_cookies(self) -> dict[str, any]:
        return self._cookies


class WordstatStream(HttpStream, ABC):
    url_base = "https://wordstat.yandex.ru/wordstat/api/"

    def __init__(self, authenticator: CookiesAuthenticator):
        super().__init__()
        self._authenticator = authenticator

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class Search(WordstatStream):
    http_method = "POST"
    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "search"

    def __init__(self, authenticator: CookiesAuthenticator, config: Mapping[str, Any]):
        super().__init__(authenticator)
        self._config: Mapping[str, Any] = config

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        # Since wordstat 2 has no public api, i will just replicate browser request
        # Some of this fields may be useless

        # TODO: нужна калибровка, но +- работает
        data: dict[str, any] = {
            "currentDevice": ",".join(self._config["device"]),
            "currentGraphType": self._config["group_by"]["group_type"],
            "filters": {
                "region": "all",  # TODO
                "tableType": "popular",
            },
            "searchValue": self._config["keyword"],
            # "startDate": self._config["time_from_transformed"].strftime("%d.%m.%Y"),
            # "endDate": self._config["time_to_transformed"].strftime("%d.%m.%Y"),
            "startDate": "24.01.2024",  # TODO
            "endDate": "23.03.2024",
        }
        return data

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        attempts_count: int = 0
        while attempts_count < 5:
            try:
                response: requests.Response = requests.post(
                    self.url_base + self.path(),
                    json=self.request_body_json(stream_state, stream_slice),
                    cookies=self._authenticator.get_cookies(),
                )
                response_json: dict[str, any] = response.json()
            except Exception as ex:  # TODO: too broad exception
                time.sleep(60)
                continue

            data: list[dict[str, any]] = response_json["graph"]["tableData"]
            for record in data:
                record["absoluteValue"] = int(record["absoluteValue"].replace(" ", ""))
                yield record
            return


class SourceWordstat(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    @staticmethod
    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")

        time_from: Optional[pendulum.datetime] = None
        time_to: Optional[pendulum.datetime] = None

        # Meaning is date but storing time since later will use time
        today_date: pendulum.datetime = pendulum.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if date_range_type == "custom_date":
            time_from = pendulum.parse(date_range["date_from"])
            time_to = pendulum.parse(date_range["date_to"])
        elif date_range_type == "from_start_date_to_today":
            time_from = pendulum.parse(date_range["date_from"])
            if date_range.get("should_load_today"):
                time_to = today_date
            else:
                time_to = today_date.subtract(days=1)
        elif date_range_type == "last_n_days":
            time_from = today_date.subtract(days=date_range.get("last_days_count"))
            if date_range.get("should_load_today"):
                time_to = today_date
            else:
                time_to = today_date.subtract(days=1)

        config["time_from_transformed"], config["time_to_transformed"] = time_from, time_to
        return config

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceWordstat.transform_config_date_range(config)
        config["cookies"] = json.loads(config["cookies"])
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth: CookiesAuthenticator = CookiesAuthenticator(cookies=config["cookies"])
        return [Search(authenticator=auth, config=config)]
