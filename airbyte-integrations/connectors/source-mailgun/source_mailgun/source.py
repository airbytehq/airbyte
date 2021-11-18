#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from pydantic import HttpUrl
from requests.auth import HTTPBasicAuth

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class MailgunStream(HttpStream, ABC):
    # TODO: Support regions (EU and US) for domains
    url_base = "https://api.mailgun.net/v3/"

    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, HttpUrl]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        next_page: Optional[HttpUrl] = response.json().get('paging', {}).get('next')
        return {"url": next_page} if next_page and self._pre_parse_response(response) else None

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Optional[Mapping[str, HttpUrl]] = None,
    ) -> str:
        # TODO: Requires improve URL creation in the CDK by using urllib.parse.urljoin
        #  (airbyte_cdk.sources.streams.http.http._create_prepared_request)
        return next_page_token["url"] if next_page_token else ""

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Optional[Mapping[str, Any]] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from self._pre_parse_response(response)

    @staticmethod
    def _pre_parse_response(response: requests.Response) -> List:
        return response.json()['items']


class Domains(MailgunStream):
    primary_key = "name"

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        # return super().path(*args, **kwargs) or "domains"  # TODO: Requires the CDK update (see MailgunStream.path())
        path: str = "domains"
        if next_page_token:
            token: str = next_page_token['url'].rpartition('/')[2]
            path = f"{path}/{token}"

        return path


# Basic incremental stream
class IncrementalMailgunStream(MailgunStream, ABC):

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        return {}


class Events(IncrementalMailgunStream):
    # TODO: Event Polling. See https://documentation.mailgun.com/en/latest/api-events.html#event-polling

    cursor_field = "timestamp"

    primary_key = "id"

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = config.get('timestamp', 0)
        self.ascending = config.get('ascending', True)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> \
            Mapping[str, Any]:
        if current_stream_state is not None and 'timestamp' in current_stream_state:
            current_parsed_timestamp = current_stream_state['timestamp']
            latest_record_timestamp = latest_record['timestamp']
            return {'timestamp': max(current_parsed_timestamp, latest_record_timestamp)}
        else:
            return {'timestamp': self.timestamp}

    def path(self, *args, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        # return super().path(*args, **kwargs) or "events"  # TODO: Requires the CDK update (see MailgunStream.path())
        path: str = "events"
        if next_page_token:
            token: str = next_page_token['url'].rpartition('/')[2]
            path = f"{path}/{token}"

        return path

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({
            "begin": stream_state.get("timestamp", self.timestamp),
            "ascending": "yes" if self.ascending else "no",
        })
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as a list of a single slice with such format:
        [{"timestamp": 1636411500.861427}]
        """
        return [stream_state]


# Source
class SourceMailgun(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            response = requests.get(urljoin(MailgunStream.url_base, 'domains'), auth=('api', config['private_key']))
            if response.status_code == 200:
                return True, None
            else:
                return False, response.json()['message']
        except requests.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HTTPBasicAuth('api', config['private_key'])

        return [Domains(authenticator=auth), Events(config=config, authenticator=auth)]
