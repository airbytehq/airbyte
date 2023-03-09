#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


class ZettleStream(HttpStream, ABC):
    def __init__(self, domain: str, config: Mapping[str, Any]):
        super().__init__()
        self._domain = domain
        self.client_id = config.get("client_id")
        self.api_key = config.get("api_key")
        self.start_date = config.get("start_date")
        self.access_token = None
        self.generate_access_token()

    def generate_access_token(self):
        oauth_url = "https://oauth.zettle.com/token"
        oauth_payload = f"grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&client_id={self.client_id}&assertion={self.api_key}"
        oauth_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        oauth_response = requests.request(
            "POST", oauth_url, headers=oauth_headers, data=oauth_payload
        )
        self.access_token = oauth_response.json().get("access_token")

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json", "Authorization": f"Bearer {self.access_token}"}

    @property
    def url_base(self) -> str:
        return f"https://{self._domain}.izettle.com"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        lastPurchaseHash = response.json().get('lastPurchaseHash')
        print('lastPurchaseHash: ', lastPurchaseHash)
        if lastPurchaseHash is not None:
            return {'lastPurchaseHash': lastPurchaseHash}
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        state_ts = pendulum.parse(stream_state.get('timestamp', self.start_date))
        start_dt = pendulum.parse(self.start_date)
        new_start_date = max(start_dt, state_ts)

        params = {
            "startDate": new_start_date.format('YYYY-MM-DD'),
            "limit": 100,
            "descending": False,
        }

        if next_page_token is not None:
            params.update({"lastPurchaseHash": next_page_token.get("lastPurchaseHash")})

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("purchases", [])


class IncrementalZettleStream(ZettleStream, ABC):
    state_checkpoint_interval = 1

    @property
    def cursor_field(self) -> str:
        """
        :return str: The name of the cursor field.
        """
        return 'timestamp'

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_state = pendulum.parse(current_stream_state.get(self.cursor_field, self.start_date))
        last_ts = pendulum.parse(latest_record.get('timestamp'))
        new_state = max(current_state, last_ts)
        return {self.cursor_field: new_state.format("YYYY-MM-DD")}


class Purchases(IncrementalZettleStream):
    endpoint_type = "purchase"
    cursor_field = "timestamp"
    primary_key = "purchaseUUID"

    def path(self, **kwargs) -> str:
        return "purchases/v2"


class SourceZettle(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Purchases(domain='purchase', config=config)]
