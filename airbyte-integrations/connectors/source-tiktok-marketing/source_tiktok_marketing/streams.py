from airbyte_cdk.sources.streams.http import HttpStream
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from airbyte_cdk.models import SyncMode
import json
import pendulum
from airbyte_cdk.sources.streams.http.auth import NoAuth
import requests


class TiktokException(Exception):
    """default exception of custom Tiktok logic"""


class ParserMixin:
    # endpoints can have different list names
    response_list_field = "list"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""

        data = response.json()
        if data["code"]:
            raise TiktokException(data["message"])
        data = data["data"]
        if self. response_list_field in data:
            data = data[self. response_list_field]
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
        # convert a start date to TikTok format
        # example:  "2021-08-24" => "2021-08-24 00:00:00"
        self._start_time = pendulum.parse(
            start_time or "1970-01-01").strftime('%Y-%m-%d 00:00:00')
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
    cursor_field = "modify_time"
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

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """returns data from API"""
        state = stream_state.get(self.cursor_field) or self._start_time
        for record in super().parse_response(response, **kwargs):
            updated = record[self.cursor_field]
            if updated <= state:
                continue
            elif not self._max_cursor_date or self._max_cursor_date < updated:
                self._max_cursor_date = updated
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        max_updated_at = self._max_cursor_date or ""
        return {self.cursor_field: max(max_updated_at, (current_stream_state or {}).get(self.cursor_field, ""))}


class Advertisers(TiktokStream):
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

    def path(self, *args, **kwargs) -> str:
        return "campaign/get/"


class AdGroups(IncrementalTiktokStream):
    primary_key = "adgroup_id"

    def path(self, *args, **kwargs) -> str:
        return "adgroup/get/"


class Ads(IncrementalTiktokStream):
    primary_key = "ad_id"

    def path(self, *args, **kwargs) -> str:
        return "ad/get/"
