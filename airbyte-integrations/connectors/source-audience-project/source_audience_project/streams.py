import logging
import pendulum
import requests
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timezone
from airbyte_cdk.sources.declarative.types import Config, Record
from typing import Any, Iterable, Mapping, Optional, Union, List, Tuple, MutableMapping

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.token import BearerAuthenticator
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement

DEFAULT_END_DATE = pendulum.yesterday().date()
DEFAULT_CAMPAIGN_STATUS = "deleted,active,archived,dirty"
DEFAULT_DATE_FLAG = False


class AudienceProjectStream(HttpStream, ABC):

    url_base = "https://campaign-api.audiencereport.com/"
    oauth_url_base = "https://oauth.audiencereport.com/"
    primary_key = ""

    def __init__(self, config: Mapping[str, Any], parent):
        super().__init__(parent)
        self.config = config
        print("self.config", self.config)
        # self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            **kwargs
    ) -> Iterable[Mapping]:
        if response.status_code == 200:
            data = response.json().get("data")
            print("response", data)
            if data:
                data["campaign_id"] = stream_slice["campaign_id"]
                yield data

    def stream_slices(
            self,
            sync_mode: SyncMode.incremental,
            cursor_field: List[str] = None,
            stream_state: Mapping[str, Any] = None,
            **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = self.parent(self._authenticator, self.config, **kwargs)
        parent_stream_slices = parent.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in parent_stream_slices:
            parent_records = parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 409:
            # self.logger.error(f"Skipping stream {self.name}. Full error message: {response.text}")
            self.logger.error(f"Skipping stream. Full error message: {response.text}")
            setattr(self, "raise_on_http_errors", False)
            return False

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""


class CampaignsStreamPagination(PageIncrement):
    max_records = 100
    start = 0

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.param = parameters
        self.start_from_page = self.start

    def next_page_token(
            self,
            response: requests.Response,
            last_records: List[Mapping[str, Any]]
    ) -> Optional[Tuple[Optional[int], Optional[int]]]:
        print("page size", self.page_size)
        print("start", self.start)
        print("start_from_page", self.start_from_page)
        print("max_records", self.max_records)
        # print("Continuous condition", self.path)
        print("len(last_records)", len(last_records))
        self.start_from_page += self.max_records
        record_len = len(last_records)
        if record_len < self.max_records or record_len == 0:
            return None
        return self.page_size, self.start_from_page


@dataclass
class CampaignsParamRequester(HttpRequester):

    @staticmethod
    def _get_time_interval(
            starting_date: Union[pendulum.datetime, str],
            ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if isinstance(starting_date, str):
            start_date = pendulum.parse(starting_date).date()
        if isinstance(ending_date, str):
            end_date = pendulum.parse(ending_date).date()
        else:
            end_date = DEFAULT_END_DATE
        if end_date < start_date:
            raise ValueError(
                f"""Provided start date has to be before end_date.
                            Start date: {start_date} -> end date: {end_date}"""
            )
        return start_date, end_date

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        print("Params", self.config)
        params = {"type": "all", "sortDirection": "asc"}
        params.update({"status": DEFAULT_CAMPAIGN_STATUS})
        date_required = self.config.get("date_flag") if self.config.get("date_flag") else DEFAULT_DATE_FLAG
        if date_required:
            stream_start, stream_end = self._get_time_interval(self.config["start_date"], self.config["end_date"])
            params.update({"creationDate": stream_start, "reportEnd": stream_end})
        if next_page_token:
            params.update(**next_page_token)
        print("Params", params)
        return params


class Campaigns(AudienceProjectStream):
    parent = ""
    config: Config

    def __init__(self, **kwargs):
        super().__init__(config=kwargs['config'], parent=self.parent)
        self.page_size = 100
        print("kwargs", kwargs)
        self.fetched_record_length = 0

    def get_page_size(self) -> Optional[int]:
        return self.page_size

    def reset(self):
        pass

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "campaigns.yml"

    def stream_slices(
        self,
        sync_mode: SyncMode.incremental,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield {}
