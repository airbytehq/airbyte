#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException
from source_telegram_ads.utils import DEFAULT_USER_AGENT
from source_telegram_ads.parser import test_logged_in, parse_all_ads, parse_ad_details, parse_ad_stats
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


# Basic full refresh stream
class TelegramAdsStream(HttpStream, ABC):
    url_base = "https://promote.telegram.org/"
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)

    def __init__(self, account_token: str, organization_token: str):
        HttpStream.__init__(self, authenticator=None)
        self._account_token = account_token
        self._organization_token = organization_token

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "user-agent": DEFAULT_USER_AGENT,
        }

    def _create_prepared_request(
        self,
        path: str,
        headers: Mapping = None,
        params: Mapping = None,
        json: Any = None,
        data: Any = None,
        cookies: Mapping = None,
    ) -> requests.PreparedRequest:
        args = {
            "method": self.http_method,
            "url": self._join_url(self.url_base, path),
            "headers": headers,
            "params": params,
            "cookies": cookies,
        }
        if self.http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data
        request = self._session.prepare_request(requests.Request(**args))
        return self._session.prepare_request(requests.Request(**args))

    def _fetch_next_page(
        self, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers, **self.authenticator.get_auth_header()),
            params=self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            cookies={
                "stel_token": self._account_token,
                "stel_adowner": self._organization_token,
            },
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        response = self._send_request(request, request_kwargs)
        return request, response

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None


class TestStream(TelegramAdsStream):
    primary_key = None

    def path(self, *args, **kwargs) -> str:
        return "account"

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        if not test_logged_in(response):
            raise Exception("Invalid credentials")
        yield True


class Ads(TelegramAdsStream):
    use_cache = True
    primary_key = "id"

    def path(self, *args, **kwargs) -> str:
        return "account"

    def parse_response(self, response: requests.Response, *args, **kwargs) -> Iterable[Mapping]:
        yield from parse_all_ads(response)


class AdsDetails(TelegramAdsStream, HttpSubStream):
    primary_key = "id"

    def __init__(self, parent: Ads, account_token: str, organization_token: str):
        TelegramAdsStream.__init__(self, account_token, organization_token)
        HttpSubStream.__init__(self, parent=parent)

    def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        return "/account/ad/" + stream_slice["parent"]["id"]

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs,
    ) -> Iterable[Mapping]:
        yield {"id": stream_slice["parent"]["id"], **parse_ad_details(response)}


class AdsStatistics(TelegramAdsStream, HttpSubStream):
    primary_key = ["ad_id", "day"]

    def __init__(self, parent: Ads, account_token: str, organization_token: str):
        TelegramAdsStream.__init__(self, account_token, organization_token)
        HttpSubStream.__init__(self, parent=parent)

    def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        ad_id = stream_slice["parent"]["id"]
        return f"account/ad/{ad_id}/stats"

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"period": "day"}

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, Any] = None,
        *args,
        **kwargs,
    ) -> Iterable[Mapping]:
        for stat in parse_ad_stats(response, self._account_token, self._organization_token):
            yield {"ad_id": stream_slice["parent"]["id"], **stat}


# Source
class SourceTelegramAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        next(
            TestStream(
                **self.get_stream_kwargs_from_config(config),
            ).read_records(sync_mode=SyncMode.full_refresh),
        )
        return True, None

    def get_stream_kwargs_from_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "account_token": config["account_token"],
            "organization_token": config["organization_token"],
        }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        shared_kwargs = self.get_stream_kwargs_from_config(config)
        ads_stream = Ads(**shared_kwargs)
        return [
            AdsDetails(parent=ads_stream, **shared_kwargs),
            AdsStatistics(parent=ads_stream, **shared_kwargs),
        ]
