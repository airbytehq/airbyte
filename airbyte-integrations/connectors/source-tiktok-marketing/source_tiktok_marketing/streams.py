#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

# Hierarchy of classes
# TiktokStream
# ├── ListAdvertiserIdsStream
# └── FullRefreshTiktokStream
#     ├── Advertisers
#     └── IncrementalTiktokStream
#         ├── AdGroups
#         ├── Ads
#         └── Campaigns

import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, TypeVar, Union

import pendulum
import pydantic
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

from .spec import DEFAULT_START_DATE

T = TypeVar("T")


class JsonUpdatedState(pydantic.BaseModel):
    current_stream_state: str
    stream: T

    def __repr__(self):
        """Overrides print view"""
        return str(self.dict())

    def dict(self, **kwargs):
        """Overrides default logic.
        A new updated stage has to be sent if all advertisers are used only
        """
        if not self.stream.is_finished:
            return self.current_stream_state
        max_updated_at = self.stream.max_cursor_date or ""
        return max(max_updated_at, self.current_stream_state)


class TiktokException(Exception):
    """default exception of custom Tiktok logic"""


class TiktokStream(HttpStream, ABC):
    # endpoints can have different list names
    response_list_field = "list"

    # max value of page
    page_size = 1000

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """All responses have the similar structure:
        {
            "message": "<OK or ERROR>",
            "code": <code>, # 0 if error else error unique code
            "request_id": "<unique_request_id>"
            "data": {
                "page_info": {
                    "total_number": <total_item_count>,
                    "page": <current_page_number>,
                    "page_size": <page_size>,
                    "total_page": <total_page_count>
                },
                "list": [
                    <list_item>
                ]
           }
        }
        """
        data = response.json()
        if data["code"]:
            raise TiktokException(data["message"])
        data = data["data"]
        if self.response_list_field in data:
            data = data[self.response_list_field]
        for record in data:
            yield record

    @property
    def url_base(self) -> str:
        """
        Docs: https://business-api.tiktok.com/marketing_api/docs?id=1701890920013825
        """
        if self.is_sandbox:
            return "https://sandbox-ads.tiktok.com/open_api/v1.2/"
        return "https://business-api.tiktok.com/open_api/v1.2/"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None

    def should_retry(self, response: requests.Response) -> bool:
        """
        Once the rate limit is met, the server returns "code": 40100
        Docs: https://business-api.tiktok.com/marketing_api/docs?id=1701890997610497
        """
        data = response.json()
        if data["code"] == 40100:
            return True
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        The system uses a second call limit for each developer app. The set limit varies according to the app's call limit level.
        """
        # Basic: 	10/sec
        # Advanced: 	20/sec
        # Premium: 	30/sec
        # All apps are set to basic call limit level by default.
        # Returns maximum possible delay
        return 0.6


class ListAdvertiserIdsStream(TiktokStream):
    """Loading of all possible advertisers"""

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
    def is_sandbox(self) -> bool:
        """
        the config parameter advertiser_id is required for Sandbox
        """
        # only sandbox has a not empty self._advertiser_id value
        return self._advertiser_id > 0

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:

        return {
            "access_token": self._access_token,
            "secret": self._secret,
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


class FullRefreshTiktokStream(TiktokStream, ABC):
    primary_key = "id"
    fields: List[str] = None

    def __init__(self, advertiser_id: int, app_id: int, secret: str, start_time: str, **kwargs):
        super().__init__(**kwargs)
        # convert a start date to TikTok format
        # example:  "2021-08-24" => "2021-08-24 00:00:00"
        self._start_time = pendulum.parse(start_time or DEFAULT_START_DATE).strftime("%Y-%m-%d 00:00:00")
        self._advertiser_storage = ListAdvertiserIdsStream(
            advertiser_id=advertiser_id, app_id=app_id, secret=secret, access_token=self.authenticator.token
        )
        self.max_cursor_date = None
        self._advertiser_ids = self._advertiser_storage.advertiser_ids

    @property
    def is_sandbox(self):
        return self._advertiser_storage.is_sandbox

    @staticmethod
    def convert_array_param(arr: List[Union[str, int]]) -> str:
        return json.dumps(arr)

    @property
    def is_finished(self):
        return len(self._advertiser_ids) == 0

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """Loads all updated tickets after last stream state"""
        while self._advertiser_ids:
            advertiser_id = self._advertiser_ids.pop(0)
            yield {"advertiser_id": advertiser_id}

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"page_size": self.page_size}
        if self.fields:
            params["fields"] = self.convert_array_param(self.fields)
        if stream_slice:
            params.update(stream_slice)
        return params


class IncrementalTiktokStream(FullRefreshTiktokStream, ABC):
    cursor_field = "modify_time"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_cursor_date = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """All responses have the following pagination data:
        {
            "data": {
                "page_info": {
                    "total_number": < total_item_count >,
                    "page": < current_page_number >,
                    "page_size": < page_size >,
                    "total_page": < total_page_count >
                },
                ...
           }
        }
        """

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
        """Additional data filtering"""
        state = stream_state.get(self.cursor_field) or self._start_time
        for record in super().parse_response(response, **kwargs):
            updated = record[self.cursor_field]
            if updated <= state:
                continue
            elif not self.max_cursor_date or self.max_cursor_date < updated:
                self.max_cursor_date = updated
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # needs to save a last state if all advertisers are used before only
        current_stream_state_value = (current_stream_state or {}).get(self.cursor_field, "")

        # a object JsonUpdatedState is related with a currect stream and should return a new updated state if needed
        if not isinstance(current_stream_state_value, JsonUpdatedState):
            current_stream_state_value = JsonUpdatedState(stream=self, current_stream_state=current_stream_state_value)

        return {self.cursor_field: current_stream_state_value}


class Advertisers(FullRefreshTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708503202263042"""

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["advertiser_ids"] = self.convert_array_param(self._advertiser_ids)
        return params

    def path(self, *args, **kwargs) -> str:
        return "advertiser/info/"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """this stream must work with the default slice logic"""
        yield None


class Campaigns(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708582970809346"""

    primary_key = "campaign_id"

    def path(self, *args, **kwargs) -> str:
        return "campaign/get/"


class AdGroups(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708503489590273"""

    primary_key = "adgroup_id"

    def path(self, *args, **kwargs) -> str:
        return "adgroup/get/"


class Ads(IncrementalTiktokStream):
    """Docs: https://ads.tiktok.com/marketing_api/docs?id=1708572923161602"""

    primary_key = "ad_id"

    def path(self, *args, **kwargs) -> str:
        return "ad/get/"
