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
from source_wordstat.auth import CookiesAuthenticator


class WordstatStream(HttpStream, ABC):
    url_base = "https://wordstat.yandex.ru/wordstat/api/"

    def __init__(
        self,
        authenticator: CookiesAuthenticator,
        config: Optional[Mapping[str, Any]] = None,
    ):
        super().__init__()
        self._authenticator = authenticator
        self._config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        attempts_count: int = 0
        body = self.request_body_json(stream_state, stream_slice)
        while attempts_count < 5:
            try:
                response: requests.Response = requests.post(
                    self.url_base + self.path(),
                    json=body,
                    cookies=self._authenticator.get_cookies(),
                )
                if response.status_code != 200:
                    raise ValueError

                # If got captcha, wordstat returns status 200
                # But json fails
                response.json()
            except Exception as ex:  # TODO: too broad exception
                time.sleep(15)
                attempts_count += 1
                continue

            for record in self.parse_response(response=response, stream_slice=stream_slice):
                yield record
            return


class Search(WordstatStream):
    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "search"

    def __init__(self, authenticator: CookiesAuthenticator, config: Mapping[str, Any]):
        super().__init__(authenticator)
        self._config: Mapping[str, Any] = config

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for keyword in self._config["keywords"]:
            yield {"keyword": keyword}

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        data: dict[str, any] = {
            "currentDevice": ",".join(self._config["device"]),
            "currentGraphType": self._config["group_type"],
            "filters": {
                "region": "all",  # TODO
                "tableType": "popular",
            },
            "searchValue": stream_slice["keyword"],
            "startDate": self._config["time_from_transformed"].strftime("%d.%m.%Y"),
            "endDate": self._config["time_to_transformed"].strftime("%d.%m.%Y"),
        }
        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json: dict[str, any] = response.json()
        stream_slice = kwargs["stream_slice"]
        for record in response_json["graph"]["tableData"]:
            record["absoluteValue"] = int(record["absoluteValue"].replace(" ", ""))
            record["value"] = float(record["value"].replace(",", "."))
            record["keyword"] = stream_slice["keyword"]
            yield record


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
        elif date_range_type == "from_start_date_to_yesterday":
            time_from = pendulum.parse(date_range["date_from"])
            time_to = today_date.subtract(days=1)
        elif date_range_type == "last_n_days":
            time_from = today_date.subtract(days=date_range.get("last_days_count"))
            time_to = today_date.subtract(days=1)

        config["time_from_transformed"], config["time_to_transformed"] = time_from, time_to
        return config

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceWordstat.transform_config_date_range(config)
        config["cookies"] = json.loads(config["cookies"])
        config["group_type"] = config["group_by"]["group_type"]

        del config["group_by"]

        # Does not support too wide intervals
        today_date: pendulum.datetime = pendulum.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if config["group_type"] == "day":
            config["time_from_transformed"] = max(config["time_from_transformed"], today_date.subtract(months=2))
        elif config["group_type"] == "week":
            config["time_from_transformed"] = max(config["time_from_transformed"], today_date.subtract(years=2))
        elif config["group_type"] == "month":
            config["time_from_transformed"] = max(config["time_from_transformed"], today_date.subtract(years=4))

        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth: CookiesAuthenticator = CookiesAuthenticator(cookies=config["cookies"])
        return [Search(authenticator=auth, config=config)]
