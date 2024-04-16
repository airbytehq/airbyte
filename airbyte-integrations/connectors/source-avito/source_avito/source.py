from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class AvitoStream(HttpStream, ABC):
    url_base = "https://api.avito.ru/"

    def __init__(self, authenticator: TokenAuthenticator):
        super().__init__(authenticator)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class CallsByTime(AvitoStream):
    http_method = "POST"
    primary_key = "id"
    record_count = 5

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "cpa/v2/callsByTime"

    def __init__(self, authenticator: TokenAuthenticator, time_from: pendulum.datetime, time_to: pendulum.datetime):
        super().__init__(authenticator)
        self.time_from: pendulum.datetime = time_from
        self.time_to: pendulum.date = time_to

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Avito api supports offset and limit but does not provide current offset (we can't store it here)
        # so will send request with start time as max startTime from all received calls
        # Just like Avito developers suggest (https://developers.avito.ru/api-catalog/cpa/documentation#operation/chatByActionId)
        response_json: dict[str, any] = response.json()
        calls: list[dict[str, any]] = response_json["result"]["calls"]
        if len(calls) < self.record_count:
            return None  # Finished all

        # Add 1 second to prevent duplicates
        max_start_time: pendulum.date = max([pendulum.parse(call["startTime"]) for call in calls]).add(seconds=1)
        if max_start_time.date() > self.time_to.date():
            return None  # Finished all by provided daterange
        else:
            return {"dateTimeFrom": max_start_time}

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        start_time: pendulum.datetime = next_page_token["dateTimeFrom"] if next_page_token else self.time_from
        data: dict[str, any] = {"limit": self.record_count, "dateTimeFrom": start_time.to_rfc3339_string()}
        return data

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json: dict[str, any] = response.json()
        if "error" in response_json:
            error_text: str = response_json["error"]["message"]
            self.logger.info(f"Request failed: {error_text}")
            raise RuntimeError("Failed to fetch data")

        if "calls" not in response_json["result"]:
            raise ValueError(response_json, response.request.body)
        for call in response_json["result"]["calls"]:
            if pendulum.parse(call["startTime"]).date() <= self.time_to.date():
                yield call


class SourceAvito(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.get_auth(config)  # Will raise exception if something is wrong
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
        config = SourceAvito.transform_config_date_range(config)
        # For future improvements
        return config

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        token_url: str = AvitoStream.url_base + "token"
        data: dict[str, str] = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "grant_type": "client_credentials",
        }
        response: requests.Response = requests.post(url=token_url, data=data)
        if not (200 <= response.status_code < 400):
            raise RuntimeError(f"Failed to get api token: status code = {response.status_code}")

        response_json: dict[str, any] = response.json()
        if "error" in response_json:
            raise RuntimeError(f"Failed to get api token: {response_json['error']['message']}")

        return TokenAuthenticator(token=response_json["access_token"])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth: TokenAuthenticator = self.get_auth(config)
        return [
            CallsByTime(
                authenticator=auth,
                time_from=config["time_from_transformed"],
                time_to=config["time_to_transformed"],
            )
        ]
