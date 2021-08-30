from airbyte_cdk.sources.streams.http import HttpStream
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from airbyte_cdk.models import SyncMode
import json
from airbyte_cdk.sources.streams.http.auth import NoAuth
import requests


class TiktokException(Exception):
    """default exception of custom Tiktok logic"""


class ParserMixin:
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""

        data = response.json()
        if data["code"]:
            raise TiktokException(data["message"])
        data = data["data"]
        if "list" in data:
            data = data["list"]
        for record in data:
            yield record

    @property
    def url_base(self) -> str:
        if self.is_sandbox:
            return "https://sandbox-ads.tiktok.com/open_api/v1.2/"
        return "https://ads.tiktok.com/open_api/v1.2/"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None


class ListAdvertiserIdsStream(ParserMixin, HttpStream):
    """Loading of all possible advertiser"""
    primary_key = "advertiser_id"

    def __init__(self, advertiser_id: int, app_id: int, secret: str, access_token: str):
        super().__init__(authenticator=NoAuth())
        self._advertiser_ids = []

        # for Sandbox env
        self._advertiser_id = advertiser_id
        if not self._advertiser_id:
            # for Production env
            self._secret = secret
            self._app_id = app_id
            self._access_token = access_token
        else:
            self._advertiser_ids.append(self._advertiser_id)

    @property
    def is_sandbox(self):
        """
        the config parameter advertiser_id is required for Sandbox
        """
        return self._advertiser_id is not None

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:

        return {
            'access_token': self._access_token,
            'secret': self._secret,
            "app_id": self._app_id,
        }

    def path(self, *args, **kwargs) -> str:
        return "oauth2/advertiser/get/"

    @property
    def advertiser_ids(self):
        if not self._advertiser_ids:
            for advertiser in self.read_records(SyncMode.full_refresh):
                self._advertiser_ids.append(advertiser["advertiser_id"])
        return self._advertiser_ids


class TiktokStream(ParserMixin, HttpStream, ABC):
    primary_key = "id"
    fields: List[str] = None

    # max value of page
    page_size = 1000

    def __init__(self, advertiser_id: int, app_id: int, secret: str, start_time: str, **kwargs):
        super().__init__(**kwargs)
        self._start_time = start_time
        self._advertiser_storage = ListAdvertiserIdsStream(
            advertiser_id=advertiser_id, app_id=app_id, secret=secret, access_token=self.authenticator.token)
        self._max_cursor_date = None

    @property
    def is_sandbox(self):
        return self._advertiser_storage.is_sandbox

    @property
    def advertiser_ids(self) -> List[int]:
        return self._advertiser_storage.advertiser_ids

    @staticmethod
    def convert_array_param(arr: List[Union[str, int]]) -> str:
        return json.dumps(arr)

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Loads all updated tickets after last stream state"""
        for advertiser_id in self.advertiser_ids:
            yield {"advertiser_id": advertiser_id}

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if self.fields:
            params["fields"]: self.convert_array_param(self.fields)
        if stream_slice:
            params.update(stream_slice)
        return params


class IncrementalTiktokStream(TiktokStream, ABC):
    # test
    page_size = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._max_cursor_date = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        page_info = response.json()["data"]["page_info"]
        if page_info["page"] < page_info["total_page"]:
            return {"page": page_info["page"] + 1}
        return None

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""
        for record in super().parse_response(**kwargs):
            if not self._max_cursor_date or self._max_cursor_date < record[self.cursor_field]:
                self._max_cursor_date = record[self.cursor_field]
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        max_updated_at = self.datetime2str(
            self._max_cursor_date) if self._max_cursor_date else ""
        return {self.cursor_field: max(max_updated_at, (current_stream_state or {}).get(self.cursor_field, ""))}


class Advertisers(TiktokStream):
    # fields = [
    #     "promotion_area", "telephone", "contacter",
    #     "currency", "phonenumber", "timezone",
    #     "id", "role", "company",
    #     "status", "description", "reason",
    #     "address", "name", "language",
    #     "industry", "license_no", "email",
    #     "license_url", "country", "balance",
    #           "create_time"
    # ]

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["advertiser_ids"] = self.convert_array_param(
            self.advertiser_ids)
        return params

    def path(self, *args, **kwargs) -> str:
        return "advertiser/info/"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Loads all updated tickets after last stream state"""
        yield None


class Campaigns(IncrementalTiktokStream):
    primary_key = "campaign_id"
    cursor_field = "modify_time"
    # fields = [
    #     "campaign_id", "campaign_name", "advertiser_id",
    #     "budget", "budget_mode", "status",
    #     "opt_status", "objective", "objective_type",
    #     "create_time", "modify_time", "is_new_structure",
    #     "split_test_variable"
    # ]

    def path(self, *args, **kwargs) -> str:
        return "campaign/get/"

    # def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
    #     """returns data from API"""

    #     data = response.json()
    #     if data["code"]:
    #         raise TiktokException(data["message"])
    #     raise Exception(data)
    #     data = data["data"]
    #     if "list" in data:
    #         data = data["list"]
    #     for record in data:
    #         yield record
