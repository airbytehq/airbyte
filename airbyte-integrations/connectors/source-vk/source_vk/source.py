#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase
from source_vk.auth import CredentialsCraftAuthenticator


# Basic full refresh stream
class VkStream(HttpStream, ABC):
    VK_API_VERSION = "5.131"
    url_base = "https://api.vk.com/method/"
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)
    pagination = False

    def __init__(self, *, authenticator: HttpAuthenticator = None, date_from: datetime, date_to: datetime):
        super().__init__(authenticator)
        self.date_from = date_from
        self.date_to = date_to

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def should_retry(self, response: requests.Response) -> bool:
        error_code = response.json().get("error", {}).get("error_code")
        return error_code in [1, 6, 9, 10, 29, 603]

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        response = super()._send(request, request_kwargs)
        if response.json().get("error") and self.should_retry(response):
            custom_backoff_time = self.backoff_time(response)
            error_message = self.error_message(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time, request=request, response=response, error_message=error_message
                )
            else:
                raise DefaultBackoffException(request=request, response=response, error_message=error_message)
        elif response.json().get("error"):
            raise Exception(self.error_message(response))
        return response

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def error_message(self, response: requests.Response) -> str:
        error = response.json().get("error", {})
        if error:
            return (
                f"Error code: {error['error_code']}, message: {error['error_msg']}, request params: {json.dumps(error['request_params'])}"
            )
        else:
            return "Unexpected error. Couldn't parse error from response"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs) -> Iterable[Mapping]:
        for record in response.json()["response"]:
            yield {**record, "group_id": stream_slice["group_id"]}


class GroupStats(VkStream):
    primary_key = ["period_from", "period_to", "group_id"]

    def __init__(
        self,
        *,
        authenticator: HttpAuthenticator = None,
        date_from: datetime,
        date_to: datetime,
        group_ids: List[int] = None,
    ):
        super().__init__(authenticator=authenticator, date_from=date_from, date_to=date_to)
        self.group_ids = group_ids

    def path(self, *args, **kwargs) -> str:
        return "stats.get"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "timestamp_from": int(self.date_from.timestamp()),
            "timestamp_to": int(self.date_to.timestamp()),
            "interval": "day",
            "group_id": stream_slice["group_id"],
            "v": self.VK_API_VERSION,
        }

    def stream_slices(self, *args, **kwargs) -> Iterable[Union[Mapping[str, Any], None]]:
        yield from [{"group_id": group_id} for group_id in self.group_ids]


# Source
class SourceVk(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self.transform_config_date_range(config)
        auth: Union[TokenAuthenticator, CredentialsCraftAuthenticator] = self.get_auth(config)

        if isinstance(auth, CredentialsCraftAuthenticator):
            success, message = auth.check_connection()
            if not success:
                return False, message

        access_denied_groups = []
        for group_id in config["group_ids"]:
            try:
                test_stream = GroupStats(
                    authenticator=auth,
                    date_from=config["date_from_transformed"],
                    date_to=config["date_to_transformed"],
                    group_ids=[group_id],
                )
                next(
                    test_stream.read_records(
                        sync_mode=SyncMode.full_refresh,
                        stream_slice={"group_id": group_id},
                    )
                )
            except Exception as e:
                if str(e).startswith("Error code"):
                    access_denied_groups.append(group_id)
        if access_denied_groups:
            return False, f"Access denied for groups: {access_denied_groups}"
        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        auth_type = config["credentials"]["auth_type"]
        if auth_type == "access_token_auth":
            return TokenAuthenticator(token=config["credentials"]["access_token"])
        elif auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                f"Invalid Auth type {auth_type}. Available: access_token_auth and credentials_craft_auth",
            )

    @staticmethod
    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")
        date_from: datetime = None
        date_to: datetime = None
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_date_format = "%Y-%m-%d"

        if date_range_type == "custom_date":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            date_to = datetime.strptime(date_range.get("date_to"), from_user_date_format)
        elif date_range_type == "from_start_date_to_today":
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

    def get_date_range(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.transform_config_date_range(config)
        shared_config = {
            "authenticator": auth,
            "date_from": config["date_from_transformed"],
            "date_to": config["date_to_transformed"],
        }
        return [GroupStats(**shared_config, group_ids=config["group_ids"])]
