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

    def __init__(self, authenticator: TokenAuthenticator, date_from: datetime.date, date_to: datetime.date, building_id: Optional[int] = None):
        super().__init__(authenticator)
        self.date_from: datetime.date = date_from
        self.date_to: datetime.date = date_to
        self.building_id: str | None = building_id

    def path(self, *args, **kwargs) -> str:
        return "v1/get-builder-calls/"

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """One slice for each request -> each day"""
        for t_delta in range((self.date_to - self.date_from).days):
            dt: datetime = datetime(year=self.date_from.year, month=self.date_from.month, day=self.date_from.day) + timedelta(days=t_delta)
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
        if 200 <= status < 400:
            yield from response_json["result"]["calls"]
        else:
            error_text: str = response_json["result"]["message"]
            self.logger.info(f"Request failed with status {status}: {error_text}")
            raise RuntimeError("Failed to fetch data")


class SourceCian(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        today_date: datetime.date = datetime.today()
        dt: datetime = datetime(year=today_date.year, month=today_date.month, day=today_date.day)
        try:
            test_stream = BuilderCalls(
                authenticator=self.get_auth(config),
                date_from=today_date,
                date_to=today_date
            )
            next(test_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"load_date": dt.isoformat()}))
            return True, None
        except StopIteration:  # Just no data for today, but everything works just fine
            return True, None
        except Exception as ex:
            return False, ex
    
    @staticmethod
    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")
        date_from: Optional[datetime] = None
        date_to: Optional[datetime] = None
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_date_format = "%Y-%m-%d"

        if date_range_type == "custom_date":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            date_to = datetime.strptime(date_range.get("date_to"), from_user_date_format)
        elif date_range_type == "from_date_from_to_today":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)
        elif date_range_type == "last_n_days":
            date_from = today_date - timedelta(date_range.get("last_days_count"))
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)

        config["date_from_transformed"], config["date_to_transformed"] = date_from, date_to
        return config

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceCian.transform_config_date_range(config)
        config["building_id"] = config.get("building_id", None)
        return config

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        return TokenAuthenticator(token=config["token"])

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth = self.get_auth(config)
        return [BuilderCalls(
            authenticator=auth,
            date_from=config["date_from_transformed"],
            date_to=config["date_to_transformed"],
            building_id=config["building_id"]
        )]
