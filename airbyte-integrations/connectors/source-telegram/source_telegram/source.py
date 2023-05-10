#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from requests import HTTPError

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class TelegramStream(HttpStream, ABC):
    url_base = "https://api.telegram.org"

    def __init__(self, authenticator: TokenAuthenticator, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.bot_token = config["bot_token"]
        self.chat_id = config["chat_id"]
        self.job_time = datetime.datetime.now()
        # chat_info = requests.get(f'{self.url_base}/2/users/by?usernames={self.screen_name}', headers=self.auth.get_auth_header())

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield {}


class ChatInfo(TelegramStream):
    primary_key = "chat_id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/bot{self.bot_token}/getChat"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"chat_id": self.chat_id}

    def read_records(
            self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()
        print('chat info result\n', result)
        if not 'result' in result.keys():
            return []

        if not result['ok']:
            return []
        info = result['result']

        return [
            {
                'chat_id': self.chat_id,
                'chat_name': info['title'],
                'type': info['type'],
                'invite_link': info['invite_link'],
                'timestamp': self.job_time,
            }
        ]
        # yield {}


class ChatMemberCount(TelegramStream):
    primary_key = "chat_id"

    def __init__(self, authenticator: TokenAuthenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(authenticator, config, **kwargs)
        self.chat_info = None
        self.chat_info_stream = ChatInfo(authenticator=None, config=config)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/bot{self.bot_token}/getChatMemberCount"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"chat_id": self.chat_id}

    def read_records(
            self, stream_slice: Optional[Mapping[str, Any]] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        try:
            print('ChatMemberCount read_records info\n')
            infos = self.chat_info_stream.read_records(stream_slice, stream_state, **kwargs)
            for info in infos:
                print('info => ', info)
                self.chat_info = info
            yield from super().read_records(**kwargs)
        except HTTPError as e:
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        result = response.json()
        print('ChatMemberCount result\n', self.chat_info, result)
        if not 'result' in result.keys():
            return []

        if not result['ok']:
            return []

        return [
            {
                'chat_id': self.chat_id,
                'chat_name': self.chat_info['chat_name'] if self.chat_info is not None and self.chat_info['chat_name'] is not None else 'None',
                'chat_member_count': result['result'],
                'timestamp': self.job_time,
            }
        ]
        # yield {}


# Source
class SourceTelegram(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        bot_token = config["bot_token"]
        chat_id = config["chat_id"]
        if bot_token and chat_id:
            return True, None
        else:
            return False, "bot_token or chat_id should not be null!"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        print("config \n", config)
        return [ChatInfo(authenticator=None, config=config), ChatMemberCount(authenticator=None,config=config)]
