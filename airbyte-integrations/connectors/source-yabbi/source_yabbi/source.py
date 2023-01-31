#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from airbyte_cdk.sources.streams.http.exceptions import RequestBodyException
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from source_yabbi.types import CampaignStatus, CampaignType, AccountAuthMethod
from source_yabbi.auth import CookiesAuthenticator, ConstantCookiesAuthenticator, CookiesNoAuth
from source_yabbi.utils import split_date_by_chunks

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class HttpStreamWithCookiesAuth(HttpStream, ABC):
    def __init__(self, authenticator: CookiesAuthenticator = None):
        self._session = requests.Session()

        if authenticator:
            self._authenticator: CookiesAuthenticator = authenticator
        else:
            self._authenticator: CookiesAuthenticator = CookiesNoAuth()

        if self.use_cache:
            self.cache_file = self.request_cache()
            self.cassete = None

    @property
    def authenticator(self) -> CookiesAuthenticator:
        return self._authenticator

    def request_cookies(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False

        next_page_token = None
        while not pagination_complete:
            request = self._create_prepared_request(
                path=self.path(stream_state=stream_state,
                               stream_slice=stream_slice, next_page_token=next_page_token),
                headers=self.request_headers(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                params=self.request_params(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                json=self.request_body_json(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                data=self.request_body_data(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
                cookies=self.request_cookies(
                    stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            )
            request_kwargs = self.request_kwargs(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

            if self.use_cache:
                with self.cache_file as cass:
                    self.cassete = cass
                    response = self._send_request(request, request_kwargs)

            else:
                response = self._send_request(request, request_kwargs)
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        yield from []

    def _create_prepared_request(
        self,
        path: str,
        headers: Mapping = None,
        params: Mapping = None,
        json: Any = None,
        data: Any = None,
        cookies: Mapping = None,
    ) -> requests.PreparedRequest:
        args = {"method": self.http_method, "url": urljoin(
            self.url_base, path), "headers": headers, "params": params, "cookies": cookies}
        if self.http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data'"
                    " and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))


class YabbiStream(HttpStreamWithCookiesAuth):
    url_base = "https://my.yabbi.me/ajax"
    method = None
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)

    def __init__(
        self,
        authenticator: CookiesAuthenticator,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None
    ):
        HttpStreamWithCookiesAuth.__init__(self, authenticator=authenticator)
        self.time_start = time_start
        self.time_end = time_end

    @abstractmethod
    def datetime_transform_method(self, dt: datetime):
        raise NotImplementedError

    def path(self, *args, **kwargs) -> str:
        return ""

    def request_cookies(
        self, *args, **kwargs
    ) -> MutableMapping[str, Any]:
        cookies = self._authenticator.get_auth_cookies()
        return cookies

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "method": self.method,
            "startTime": self.datetime_transform_method(self.time_start),
            "endTime": self.datetime_transform_method(self.time_end),
        }

    def check_response_for_errors(self, response: requests.Response):
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            if '/login?method=account' in response.text:
                raise Exception("Unauthorized")
            else:
                raise Exception(response.text)

        if isinstance(data, dict) and "err" in data.keys():
            raise Exception(
                f"API Exception for URL {response.request.url}: {response.text}")

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print(response.request.url)

        self.check_response_for_errors(response)
        objects_list = response.json()
        if objects_list == None:
            objects_list = []
        yield from objects_list


class AgencyAccounts(YabbiStream):
    primary_key = "id"
    method = ""
    url_base = "https://my.yabbi.me/agency-ajax"
    method = "allAccounts"
    use_cache = True

    def __init__(self, authenticator: CookiesAuthenticator):
        time_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
        super().__init__(authenticator, time_start, time_end)

    def datetime_transform_method(self, dt: datetime):
        return int(dt.timestamp()) * 1000


class Campaigns(YabbiStream):
    primary_key = "id"
    method = "campaign-list"

    def __init__(
        self,
        authenticator: CookiesAuthenticator,
        time_start: datetime,
        time_end: datetime,
        campaigns_status: CampaignStatus = CampaignStatus.ALL,
        campaigns_type: CampaignType = CampaignType.ALL,
    ):
        super().__init__(
            authenticator=authenticator,
            time_start=time_start,
            time_end=time_end
        )
        self.campaigns_status = campaigns_status
        self.campaigns_type = campaigns_type

    @staticmethod
    def datetime_transform_method(dt: datetime):
        return int(dt.timestamp() * 1000)

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(*args, **kwargs)
        return {
            **params,
            "status": self.campaigns_status.value,
            "type": self.campaigns_type.value,
        }


class Banners(YabbiStream, HttpSubStream):
    method = 'campaign-banner'
    primary_key = "id"

    def __init__(
        self,
        authenticator: CookiesAuthenticator,
        campaigns_stream_instance: Campaigns,
    ):
        HttpSubStream.__init__(self, parent=campaigns_stream_instance)
        YabbiStream.__init__(
            self,
            authenticator=authenticator
        )

    @staticmethod
    def datetime_transform_method(dt: datetime):
        return dt.strftime('%a, %d %b %Y %H:%M:%S %Z')

    def request_params(self, stream_slice: Mapping[str, any] = None, *args, **kwargs) -> MutableMapping[str, Any]:
        return {
            "method": self.method,
            "id": stream_slice['parent']['id']
        }


class BannersStatistics(YabbiStream, HttpSubStream):
    method = 'statistics-banner'
    primary_key = ["id"]

    def __init__(
        self,
        authenticator: CookiesAuthenticator,
        campaigns_stream_instance: Campaigns,
        time_start: Optional[datetime] = None,
        time_end: Optional[datetime] = None
    ):
        HttpSubStream.__init__(self, parent=campaigns_stream_instance)
        YabbiStream.__init__(
            self,
            authenticator=authenticator,
            time_start=time_start,
            time_end=time_end
        )

    @staticmethod
    def datetime_transform_method(dt: datetime):
        return dt.strftime('%a, %d %b %Y %H:%M:%S %Z GMT')

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "id": stream_slice['parent']['id']
        }
        params.pop("startTime"), params.pop("endTime")
        date_from, date_to = stream_slice["days_chunk"]
        params["timeStart"], params["timeEnd"] = self.datetime_transform_method(
            date_from), self.datetime_transform_method(date_to)
        return params

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs) -> Iterable[Mapping]:
        self.check_response_for_errors(response)

        data: dict[str, Any] = response.json()
        date_from, date_to = stream_slice["days_chunk"]
        for banner_id, stat in data.items():
            yield {
                "id": banner_id,
                "date_from": date_from,
                "date_to": date_to,
                **stat
            }

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for slice in super().stream_slices(
            sync_mode=sync_mode,
            cursor_field=cursor_field,
            stream_state=stream_state
        ):
            for days_chunk in split_date_by_chunks(
                date_from=self.time_start,
                date_to=self.time_end,
                chunk_size_in_days=1
            ):
                yield {**slice, "days_chunk": days_chunk}


class SourceYabbi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.get_auth(config)
        return True, None

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        time_range = config["time_range"]
        range_type = config["time_range"]["time_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_time":
            prepared_range["time_start"] = time_range["time_start"]
            prepared_range["time_end"] = time_range["time_end"]
        elif range_type == "from_start_time_to_today":
            prepared_range["time_start"] = time_range["time_start"]
            if time_range["should_load_today"]:
                prepared_range["time_end"] = today
            else:
                prepared_range["time_end"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["time_start"] = today - \
                timedelta(days=time_range["last_days_count"])
            if time_range["should_load_today"]:
                prepared_range["time_end"] = today
            else:
                prepared_range["time_end"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid time_range_type")

        if isinstance(prepared_range["time_start"], str):
            prepared_range["time_start"] = datetime.strptime(
                prepared_range["time_start"], TIME_FORMAT)

        if isinstance(prepared_range["time_end"], str):
            prepared_range["time_end"] = datetime.strptime(
                prepared_range["time_end"], TIME_FORMAT)
        config["prepared_time_range"] = prepared_range
        return config

    def get_auth(self, config: Mapping[str, Any]) -> CookiesAuthenticator:
        auth_config: dict[str, Any] = config['auth']
        if auth_config['auth_type'] == 'login_password_auth':

            cookies_auth_kwargs = dict(
                auth_cookies_refresh_endpoint="https://my.yabbi.me/login",
                get_auth_cookies_request_params={
                    "method": auth_config["account_type"]
                },
                get_auth_cookies_request_data={
                    "login": auth_config["login"],
                    "password": auth_config["password"]
                },
                get_auth_cookies_request_headers={
                    "referer": "https://my.yabbi.me/login?method=agency",
                },
            )
            agency_auth = CookiesAuthenticator(
                **cookies_auth_kwargs
            )
            auth = agency_auth

            if auth_config.get('account_login'):
                lookup_account_login = auth_config.get('account_login')
                agency_accounts = list(AgencyAccounts(authenticator=agency_auth).read_records(
                    sync_mode=SyncMode.full_refresh))

                found_agency_account = None

                for agency_account in agency_accounts:
                    if agency_account['login'] == lookup_account_login:
                        found_agency_account = agency_account

                if not found_agency_account:
                    available_accounts_s = ', '.join(
                        [
                            account_record['login']
                            for account_record in agency_accounts
                        ]
                    )
                    raise Exception(
                        f"Account {lookup_account_login} not found. Available: {available_accounts_s}")

                auth = CookiesAuthenticator(
                    auth_cookies_refresh_endpoint="https://my.yabbi.me/agency",
                    get_auth_cookies_request_params={
                        "method": "loginAccount",
                        "id": found_agency_account['id'],
                        "login": found_agency_account['login']
                    },
                    get_auth_cookies_request_headers={
                        "referer": "https://my.yabbi.me/agency?method=accounts",
                    },
                    get_auth_cookies_request_method="GET",
                    first_layer_authentiator=agency_auth
                )

        elif auth_config["auth_type"] == "constant_cookies_auth":
            constant_cookies = {
                "as-account-session": auth_config['account_access_token'],
            }
            if auth_config.get('agency_access_token'):
                constant_cookies["as-agency-session"] = auth_config.get(
                    'agency_access_token')

            if auth_config.get('as_account_cookie'):
                constant_cookies["as-account"] = auth_config.get(
                    'as_account_cookie')

            auth = ConstantCookiesAuthenticator(auth_cookies=constant_cookies)

        else:
            raise Exception(
                f"Invalid auth_type \"{config['auth_type']}\"."
                " Available: \"login_password_auth\", \"constant_cookies_auth\""
            )
        return auth

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.prepare_config_datetime(config)
        shared_kwargs = dict(
            authenticator=self.get_auth(config)
        )
        time_kwargs = dict(
            time_start=config['prepared_time_range']['time_start'],
            time_end=config['prepared_time_range']['time_end'],
        )
        campaigns_stream_instance = Campaigns(**shared_kwargs, **time_kwargs)

        streams = [
            campaigns_stream_instance,
            Banners(
                **shared_kwargs,
                campaigns_stream_instance=campaigns_stream_instance
            ),
            BannersStatistics(
                **shared_kwargs,
                **time_kwargs,
                campaigns_stream_instance=campaigns_stream_instance
            )
        ]

        if config.get("auth", {}).get("account_type") == "agency":
            streams.append(AgencyAccounts(**shared_kwargs))

        return streams
