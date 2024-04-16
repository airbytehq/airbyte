#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union, Iterable

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .auth import CredentialsCraftAuthenticator, CalltouchAuthenticator


# Basic full refresh stream
class CalltouchStream(HttpStream, ABC):
    url_base = "https://api.calltouch.ru/"
    limit = 1000

    def __init__(self, authenticator: Union[CredentialsCraftAuthenticator, CalltouchAuthenticator], date_from: datetime, date_to: datetime):
        super().__init__(authenticator=None)
        self._authenticator = authenticator
        self._date_from: datetime = date_from
        self._date_to: datetime = date_to

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        last_response_data = response.json()
        if not last_response_data:
            return None

        if last_response_data["pageTotal"] > last_response_data["page"]:
            next_page = {"next_page": response.json()["page"] + 1}
        else:
            next_page = None
        return next_page

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        next_page = next_page_token.get("next_page") if next_page_token else 1
        params = {
            "clientApiId": self._authenticator.token,
            "dateFrom": self.process_time(self._date_from),
            "dateTo": self.process_time(self._date_to),
            "page": next_page,
            "limit": self.limit,
        }
        return params

    @staticmethod
    def process_time(dt: datetime) -> str:
        """Some of calltouch streams have different time format for some reason"""
        return dt.strftime("%d/%m/%Y")


class Calls(CalltouchStream):
    primary_key = "callId"

    def __init__(
        self,
        authenticator: Union[CredentialsCraftAuthenticator, CalltouchAuthenticator],
        date_from: datetime,
        date_to: datetime,
        site_id: str,
        calls_bind_to: str | None,
        calls_attribution: int | None,
    ):
        super().__init__(authenticator, date_from, date_to)
        self._site_id: str = site_id
        self._calls_bind_to: str | None = calls_bind_to
        self._calls_attribution: int | None = calls_attribution

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["withCallTags"] = True

        if self._calls_bind_to:
            params["bindTo"] = self._calls_bind_to

        if self._calls_attribution:
            params["attribution"] = self._calls_attribution

        return params

    def path(self, **kwargs) -> str:
        return f"calls-service/RestAPI/{self._site_id}/calls-diary/calls"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()["records"]


class Requests(CalltouchStream):
    primary_key = "requestId"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(
            **kwargs,
        )
        params["withRequestTags"] = True
        return params

    def path(self, **kwargs) -> str:
        return f"calls-service/RestAPI/requests"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()

    @staticmethod
    def process_time(dt: datetime) -> str:
        """Some of calltouch streams have different time format for some reason"""
        return dt.strftime("%m/%d/%Y")


# Source
class SourceCalltouch(AbstractSource):

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> Union[CalltouchAuthenticator, CredentialsCraftAuthenticator]:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return CalltouchAuthenticator(token=config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception("Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        calls_stream = self.streams(config)[0]
        try:
            yesterday_date_str = (datetime.now() - timedelta(1)).date().strftime("%d/%m/%Y")
            stream_params = calls_stream.request_params().copy()
            stream_params["limit"] = 1
            stream_params["dateFrom"] = yesterday_date_str
            stream_params["dateTo"] = yesterday_date_str
            test_response = requests.get(calls_stream.url_base + calls_stream.path(), params=stream_params)
            if test_response.status_code != 200:
                return False, test_response.text
            else:
                return True, None
        except Exception as e:
            return False, e

    @staticmethod
    def transform_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Transform config date ranges"""
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")
        date_from: Optional[datetime] = None
        date_to: Optional[datetime] = None
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

        config["dateTo"] = date_to
        config["dateFrom"] = date_from

        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self.transform_config(config)
        auth = self.get_auth(config)
        return [
            Calls(
                authenticator=auth,
                date_from=config["dateFrom"],
                date_to=config["dateTo"],
                site_id=config["site_id"],
                calls_attribution=config.get("calls_attribution"),
                calls_bind_to=config.get("callsBindTo"),
            ),
            Requests(authenticator=auth, date_from=config["dateFrom"], date_to=config["dateTo"]),
        ]
