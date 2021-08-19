from airbyte_cdk.sources.streams.http import HttpStream
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from airbyte_cdk.models import SyncMode
import requests


class TiktokMarketingException(Exception):
    """default exception of custom TiktokMarketing logic"""


class TiktokMarketingStream(HttpStream, ABC):
    def __init__(self, is_sandbox: bool, start_time: str, **kwargs):
        super().__init__(**kwargs)
        self._is_sandbox = is_sandbox
        self._start_time = start_time

    @property
    def url_base(self) -> str:
        if self._is_sandbox:
            return "https://sandbox-ads.tiktok.com/open_api/v1.2/"
        return "https://ads.tiktok.com/open_api/v1.2/"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        # this data without listing
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """returns data from API"""

        data = response.json()
        if data["code"]:
            raise TiktokMarketingException(data["message"])

        raise Exception(data)
        settings = response.json().get("settings")
        if settings:
            yield settings


class PermissionStream(TiktokMarketingStream):
    primary_key = "aaa"

    def request_params(
        self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        fields = ["promotion_area", "telephone", "contacter", "currency", "phonenumber", "timezone", "id", "role",
                  "company", "status", "description", "reason",
                  "address", "name", "language", "industry", "license_no", "email", "license_url", "country", "balance", "create_time"
                  ]

        return {
            "fields": '["%s"]' % '","'.join(fields),
            "advertiser_ids": "[\"6997878802407784449 \"]"
            # 'access_token': self.authenticator._token,
            # 'secret': "4623eb6245fd166ddd1cfb226ca872f3cf6badb4",
            # "app_id": "6995091118178172929",
        }

    def get_settings(self) -> Mapping[str, Any]:
        return next(self.read_records(SyncMode.full_refresh))
        # for resp in:
        #     return resp
        # raise TiktokMarketingException("not found settings")

    def path(self, *args, **kwargs) -> str:
        # return "oauth2/advertiser/get/"
        return "advertiser/info/"
        return "user/info/"
