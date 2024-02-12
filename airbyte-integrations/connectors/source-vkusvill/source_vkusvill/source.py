#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
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


class PaginationStream(VkusvillStream, ABC):
    page_size = 100
    data_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        headers = response.json()["Headers"]
        total_pages = headers["x-pagination-page-count"][0]
        current_page = headers["x-pagination-current-page"][0]

        next_page = current_page + 1
        # REMOVE - for testing
        if current_page == 3:
            next_page = None

        if total_pages == 0 or current_page == total_pages:
            next_page = None

        logger.info(f"total_pages: {total_pages}, next_page: {next_page}")

        if next_page is None:
            return None
        return {"next_page_token": current_page + 1}

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
        if next_page_token:
            params["page_token"] = next_page_token["next_page_token"]
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


class Candidates(PaginationStream, IncrementalMixin):
    # OK
    use_cache = True
    primary_key = "id"
    data_key = "candidate_list"
    cursor_field = "updated_at"

    def path(self, *args, **kwargs) -> str:
        return "candidates"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "sort": "-updated_at",
            # "filter[created_at][>]": "2023-12-25",
        }

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value[self.cursor_field]


class DataLogs(PaginationStream):
    # OK
    primary_key = "id"

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

    def path(self, *args, **kwargs) -> str:
        return "dictionary-values"


class Flows(PaginationStream):
    # OK
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "flows"


class Requests(PaginationStream):
    # OK
    primary_key = "id"
    use_cache = True
    data_key = "request_list"

    def path(self, *args, **kwargs) -> str:
        return "requests"


class Resumes(PaginationStream):
    # OK
    primary_key = "id"

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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        shared_kwargs = dict(authenticator=auth, url_base=config["url_base"])

        candidates_stream = Candidates(**shared_kwargs)
        requests_stream = Requests(**shared_kwargs)
        vacancies_stream = Vacancies(**shared_kwargs)
        dictionaries_stream = Dictionaries(**shared_kwargs)
        return [
            candidates_stream,
            requests_stream,
            vacancies_stream,
            dictionaries_stream,
            DataLogs(**shared_kwargs),
            CandidateInterviewStory(**shared_kwargs, parent=candidates_stream),
            CandidateStageCounters(**shared_kwargs),
            CandidateTags(**shared_kwargs),
            DictionaryDropdowns(**shared_kwargs, parent=dictionaries_stream),
            DictionaryDropdownGroups(**shared_kwargs),
            DictionaryOptions(**shared_kwargs),
            DictionaryValues(**shared_kwargs),
            Flows(**shared_kwargs),
            Resumes(**shared_kwargs),
            Stages(**shared_kwargs),
            StageTypes(**shared_kwargs),
            StageStates(**shared_kwargs),
            StageStateSelf(**shared_kwargs),
            Stores(**shared_kwargs),
            Users(**shared_kwargs),
            VacancyCandidates(**shared_kwargs, parent=vacancies_stream),
        ]
