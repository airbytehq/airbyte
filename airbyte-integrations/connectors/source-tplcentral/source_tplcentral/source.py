#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from typing import (Any, Iterable, List, Mapping, MutableMapping, Optional,
                    Tuple)
from urllib.parse import parse_qsl, urlparse
import arrow

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import \
    Oauth2Authenticator
from requests.auth import HTTPBasicAuth

from .util import normalize


# Basic full refresh stream
class TplcentralStream(HttpStream, ABC):
    url_base = None

    def __init__(self, config) -> None:
        super().__init__(authenticator=config['authenticator'])

        self.url_base = config['url_base']
        self.customer_id = config.get('customer_id', None)
        self.facility_id = config.get('facility_id', None)
        self.start_date = config.get('start_date', None)

        if self.start_date is not None:
            self.start_date = arrow.get(self.start_date)

        self.total_results_field = "TotalResults"

    @property
    def page_size(self):
        None

    def next_page_token(self, response: requests.Response, **kwargs) -> Optional[Mapping[str, Any]]:
        data = response.json()
        total = data[self.total_results_field]

        pgsiz = self.page_size or len(data[self.collection_field])

        url = urlparse(response.request.url)
        qs = dict(parse_qsl(url.query))

        pgsiz = int(qs.get('pgsiz', pgsiz))
        pgnum = int(qs.get('pgnum', 1))

        if pgsiz * pgnum >= total:
            return None

        return {
            'pgsiz': pgsiz,
            'pgnum': pgnum + 1,
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()


class StockSummaries(TplcentralStream):
    primary_key = ["facility_id", ["item_identifier", "id"]]
    page_size = 500
    collection_field = "Summaries"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "inventory/stocksummaries"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [normalize(v) for v in response.json()['Summaries']]


class IncrementalTplcentralStream(TplcentralStream, ABC):
    state_checkpoint_interval = 10

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state is not None and "cursor" in current_stream_state:
            current_date = arrow.get(current_stream_state["cursor"])
            latest_record_date = arrow.get(latest_record["cursor"])
            return {
                "cursor": max(current_date, latest_record_date).isoformat()
            }
        return {
            "cursor": self.start_date.isoformat()
        }


class Items(IncrementalTplcentralStream):
    primary_key = "cursor"
    cursor_field = "cursor"

    collection_field = "ResourceList"

    def path(self, **kwargs) -> str:
        return f"customers/{self.customer_id}/items"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_date = arrow.get(stream_state["cursor"]) if stream_state and "date" in stream_state else self.start_date
        return [{
            "cursor": start_date
        }]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = next_page_token.copy() if isinstance(next_page_token, dict) else {}

        if self.cursor_field:
            cursor = stream_slice.get(self.cursor_field, None)
            if cursor:
                params.update({
                    "rql": f"ReadOnly.lastModifiedDate=ge={cursor}",
                })

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        out = []
        for v in response.json()['ResourceList']:
            v = normalize(v)
            v['cursor'] = v['read_only']['last_modified_date']
            out.append(v)
        return out


class TplcentralAuthenticator(Oauth2Authenticator):
    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        user_login_id: int = None,
        user_login: str = None,
    ):
        super().__init__(
            token_refresh_endpoint=token_refresh_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=None,
        )

        self.user_login_id = user_login_id
        self.user_login = user_login

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        if self.user_login_id:
            payload["user_login_id"] = self.user_login_id

        if self.user_login:
            payload["user_login"] = self.user_login

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.post(
                self.token_refresh_endpoint,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                json=self.get_refresh_request_body()
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.access_token_name], response_json[self.expires_in_name]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceTplcentral(AbstractSource):
    def _auth(self, config):
        return TplcentralAuthenticator(
            token_refresh_endpoint=f"{config['url_base']}AuthServer/api/Token",
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            user_login_id=config.get('user_login_id', None),
            user_login=config.get('user_login', None),
        )

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            self._auth(config).get_auth_header()
        except Exception as e:
            return None, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config['authenticator'] = self._auth(config)

        return [
            StockSummaries(config),
            Items(config),
        ]
