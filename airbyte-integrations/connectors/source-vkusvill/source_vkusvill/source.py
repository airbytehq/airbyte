#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_vkusvill.auth import VkusvillPasswordAuth
from source_vkusvill.utils import seconds_to_humantime

logger = logging.getLogger("airbyte")


# Basic full refresh stream
class VkusvillStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization,
    )
    data_key = None

    def __init__(self, authenticator: TokenAuthenticator, url_base: str):
        super().__init__(authenticator)
        self._url_base_input = url_base.rstrip("/")

    @property
    def url_base(self):
        return self._url_base_input + "/api/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class PaginationStream(VkusvillStream, IncrementalMixin, ABC):
    page_size = 100
    cursor_field = None
    cursor_field_in_record = None

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        url_base: str,
        date_from: datetime,
        date_to: datetime,
        is_incremental: bool,
    ):
        super().__init__(authenticator, url_base)
        self.date_from = date_from
        self.date_to = date_to
        self.is_incremental = is_incremental
        self._state = {}

    @property
    def state_checkpoint_interval(self) -> int:
        return self.page_size

    @property
    def supports_incremental(self) -> bool:
        return (
            self.is_incremental
            and self.cursor_field is not None
            and self.date_to is None
            and self.date_from is not None
        )

    @property
    def state(self):
        if not self._state:
            print("self.cursor_field", self.cursor_field)
            self._state = {self.cursor_field: self.dt_to_source_format(self.date_from)}
        return self._state

    @staticmethod
    def dt_to_source_format(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def source_format_to_dt(dt: str) -> datetime:
        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self.supports_incremental:
                current_cursor_value = self.source_format_to_dt(self.state[self.cursor_field])
                latest_cursor_value = self.in_record_date_str_to_dt(
                    record[self.cursor_field_in_record]
                )
                new_cursor_value = max(latest_cursor_value, current_cursor_value)
                self.state = {self.cursor_field: self.dt_to_source_format(new_cursor_value)}
            yield record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        headers = response.json()["Headers"]
        total_pages = headers["x-pagination-page-count"][0]
        current_page = headers["x-pagination-current-page"][0]

        next_page = current_page + 1

        if total_pages == 0 or current_page == total_pages:
            next_page = None

        logger.info(f"total_pages: {total_pages}, next_page: {next_page}")

        if next_page is None:
            return None
        return {"next_page_token": current_page + 1}

    def in_record_date_str_to_dt(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        page = 1 if not next_page_token else next_page_token["next_page_token"]

        params = {
            "per-page": self.page_size,
            "page": page,
        }
        if self.cursor_field:
            params = {**params, **self.build_params_filter(stream_state)}

        if next_page_token:
            params["page_token"] = next_page_token["next_page_token"]
        return params

    def build_params_filter(
        self,
        stream_state: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        params = {}
        sort_value = stream_state.get(self.cursor_field, self.date_from)
        if isinstance(sort_value, datetime):
            sort_value = self.dt_to_source_format(sort_value)
        params["sort"] = self.cursor_field
        params[f"filter[{self.cursor_field}][>]"] = sort_value
        return params

    @classmethod
    def log_estimate_stream_time(cls, response: requests.Response):
        """Log current response load time, and estimated time to load the whole stream"""
        load_time = response.elapsed.total_seconds()
        headers = response.json().get("Headers")

        if not headers:
            return

        total_pages = headers["x-pagination-page-count"][0]
        current_page = headers["x-pagination-current-page"][0]
        estimated_time = load_time * (total_pages - current_page)
        total_records_count = total_pages * cls.page_size
        logger.info(
            f"Loaded page {current_page} of {total_pages} in {load_time} seconds. "
            "Estimated time to load the whole stream: "
            f"{seconds_to_humantime(estimated_time)} seconds "
            f"(about {total_records_count} records)."
        )

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        self.log_estimate_stream_time(response)
        if not self.data_key:
            yield from response.json()["DATA"]
        else:
            yield from response.json()["DATA"][self.data_key]


class Candidates(PaginationStream):
    # OK
    use_cache = True
    primary_key = "id"
    data_key = "candidate_list"
    cursor_field = "updated_at"
    cursor_field_in_record = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "candidates"


class DataLogs(PaginationStream):
    # OK
    primary_key = "id"
    cursor_field = "date"
    cursor_field_in_record = "date"

    def in_record_date_str_to_dt(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M")

    def build_params_filter(
        self,
        stream_state: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        # build between[created_at]=01.02.2024-02.02.2024
        params = {}
        from_value = stream_state.get(self.cursor_field, self.date_from)
        if isinstance(from_value, datetime):
            from_value = self.dt_to_source_format(from_value)

        to_value = self.date_to or datetime.now()
        if isinstance(from_value, datetime):
            to_value = self.dt_to_source_format(from_value)
        params["sort"] = self.cursor_field
        params[f"between[{self.cursor_field}]"] = f"{from_value}-{to_value}"
        return params

    def path(self, *args, **kwargs) -> str:
        return "data-logs"


class CandidateInterviewStory(VkusvillStream, HttpSubStream):
    # OK
    primary_key = "id"

    def __init__(self, authenticator: TokenAuthenticator, url_base: str, parent: Candidates):
        VkusvillStream.__init__(self, authenticator=authenticator, url_base=url_base)
        HttpSubStream.__init__(
            self,
            parent=parent,
            authenticator=authenticator,
        )

    def path(self, *args, **kwargs) -> str:
        return "candidate/get-interview-story"

    def request_params(
        self, stream_slice: Mapping[str, any] = None, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"candidate_id": stream_slice["parent"]["id"]}
        return params

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs
    ) -> Iterable[Mapping]:
        parent_id = stream_slice["parent"]["id"]
        yield from (
            {
                **record,
                "candidate_id": parent_id,
            }
            for record in response.json()["DATA"]
        )


class CandidateStageCounters(VkusvillStream):
    # OK
    primary_key = "stage_id"

    def path(self, *args, **kwargs) -> str:
        return "candidate/get-stage-counters"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["DATA"]


class CandidateTags(PaginationStream):
    # OK
    primary_key = "candidate_id"

    def path(self, *args, **kwargs) -> str:
        return "candidate-tags"


class Dictionaries(PaginationStream):
    # OK
    primary_key = "id"
    use_cache = True

    def path(self, *args, **kwargs) -> str:
        return "dictionaries"


class DictionaryDropdowns(VkusvillStream, HttpSubStream):
    # OK
    primary_key = "dictionary_key"

    def __init__(self, authenticator: TokenAuthenticator, url_base: str, parent: Dictionaries):
        VkusvillStream.__init__(self, authenticator=authenticator, url_base=url_base)
        HttpSubStream.__init__(
            self,
            parent=parent,
            authenticator=authenticator,
        )

    def path(self, *args, **kwargs) -> str:
        return "dictionary/get-drop-down"

    def request_params(
        self, stream_slice: Mapping[str, any] = None, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"keys": "&".join(stream_slice["keys"]), "clearCache": 1}
        return params

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield {
            "keys": [
                record["parent"]["key"]
                for record in super().stream_slices(sync_mode, cursor_field, stream_state)
            ]
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        try:
            for dict_key in response.json()["DATA"].keys():
                yield {
                    "dictionary_key": dict_key,
                    "options": response.json()["DATA"][dict_key],
                }
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            yield from []


class DictionaryDropdownGroups(VkusvillStream):
    # OK
    primary_key = []

    def path(self, *args, **kwargs) -> str:
        return "dictionary/get-drop-down-group"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["DATA"]


class DictionaryOptions(PaginationStream):
    # OK
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "dictionary-options"


class DictionaryValues(PaginationStream):
    # OK
    primary_key = "id"
    cursor_field_in_record = "updated_at"
    cursor_field = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "dictionary-values"


class Flows(PaginationStream):
    # OK
    primary_key = "id"
    cursor_field_in_record = "created_at"
    cursor_field = "created_at"

    def path(self, *args, **kwargs) -> str:
        return "flows"


class Requests(PaginationStream):
    # OK
    primary_key = "id"
    use_cache = True
    data_key = "request_list"
    cursor_field_in_record = "updated_at"
    cursor_field = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "requests"


class Resumes(PaginationStream):
    # OK
    primary_key = "id"
    cursor_field_in_record = "updated_at"
    cursor_field = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "resumes"


class Stages(PaginationStream):
    # OK
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "stages"


class StageTypes(VkusvillStream):
    # OK
    primary_key = None

    def path(self, *args, **kwargs) -> str:
        return "stage/get-types"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["DATA"]


class StageStates(PaginationStream):
    # OK
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "stage-states"


class StageStateSelf(VkusvillStream):
    # OK
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "stage-state/self"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["DATA"]


class Stores(PaginationStream):
    # OK
    primary_key = "id"
    cursor_field_in_record = "updated_at"
    cursor_field = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "stores"


class Users(PaginationStream):
    # OK
    primary_key = None

    def path(self, *args, **kwargs) -> str:
        return "users"


class Vacancies(PaginationStream):
    # OK
    primary_key = "id"
    use_cache = True
    data_key = "vacancy_list"

    def path(self, *args, **kwargs) -> str:
        return "vacancies"


class VacancyCandidates(VkusvillStream, HttpSubStream):
    # OK

    primary_key = "id"

    def __init__(self, authenticator: TokenAuthenticator, url_base: str, parent: Vacancies):
        VkusvillStream.__init__(self, authenticator=authenticator, url_base=url_base)
        HttpSubStream.__init__(
            self,
            parent=parent,
            authenticator=authenticator,
        )

    def path(self, *args, **kwargs) -> str:
        return "vacancy/candidates"

    def request_params(
        self, stream_slice: Mapping[str, any] = None, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"vacancy_id": stream_slice["parent"]["id"]}
        return params

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs
    ) -> Iterable[Mapping]:
        parent_id = stream_slice["parent"]["id"]
        yield from (
            {
                **record,
                "vacancy_id": parent_id,
            }
            for record in response.json()["DATA"]
        )


# Source
class SourceVkusvill(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.get_auth(config)
        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        return VkusvillPasswordAuth(
            config["url_base"],
            config["credentials"]["username"],
            config["credentials"]["password"],
        )

    @staticmethod
    def parse_date_string(date_string: str) -> Optional[datetime]:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["date_from_transformed"], config["date_to_transformed"] = None, None
        config["use_incremental"] = False
        if config["date_range"]["date_range_type"] == "incremental_sync":
            if user_date_from := config["date_range"].get("date_from"):
                config["date_from_transformed"] = self.parse_date_string(user_date_from)
            else:
                config["date_from_transformed"] = datetime.fromtimestamp(0)
            config["date_to_transformed"] = None
            config["use_incremental"] = True
        elif config["date_range"]["date_range_type"] == "custom_date":
            config["date_from_transformed"] = self.parse_date_string(
                config["date_range"]["date_from"]
            )
            config["date_to_transformed"] = self.parse_date_string(config["date_range"]["date_to"])
        elif config["date_range"]["date_range_type"] == "last_days":
            delta = int(config["date_range"]["last_days_count"])
            config["date_to_transformed"] = datetime.now().replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            if config["date_range"].get("load_today", False):
                config["date_to_transformed"] = config["date_to_transformed"] - timedelta(days=1)
            config["date_from_transformed"] = config["date_to_transformed"] - timedelta(days=delta)
        else:
            raise ValueError("Invalid date_range_type")

        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.transform_config(config)
        shared_kwargs = dict(authenticator=auth, url_base=config["url_base"])
        pagination_kwargs = dict(
            **shared_kwargs,
            date_from=config["date_from_transformed"],
            date_to=config["date_to_transformed"],
            is_incremental=config["use_incremental"],
        )

        candidates_stream = Candidates(**pagination_kwargs)
        requests_stream = Requests(**pagination_kwargs)
        vacancies_stream = Vacancies(**pagination_kwargs)
        dictionaries_stream = Dictionaries(**pagination_kwargs)
        return [
            candidates_stream,
            requests_stream,
            vacancies_stream,
            dictionaries_stream,
            DataLogs(**pagination_kwargs),
            CandidateInterviewStory(**shared_kwargs, parent=candidates_stream),
            CandidateStageCounters(**shared_kwargs),
            CandidateTags(**pagination_kwargs),
            DictionaryDropdowns(**shared_kwargs, parent=dictionaries_stream),
            DictionaryDropdownGroups(**shared_kwargs),
            DictionaryOptions(**pagination_kwargs),
            DictionaryValues(**pagination_kwargs),
            Flows(**pagination_kwargs),
            Resumes(**pagination_kwargs),
            Stages(**pagination_kwargs),
            StageTypes(**shared_kwargs),
            StageStates(**pagination_kwargs),
            StageStateSelf(**shared_kwargs),
            Stores(**pagination_kwargs),
            Users(**pagination_kwargs),
            VacancyCandidates(**shared_kwargs, parent=vacancies_stream),
        ]
