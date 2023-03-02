from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


__all__ = [
    'ProjectSyncStream',
    'FinanceStream',
    'StaffTrackStream'
]


class ProjectSyncStream(HttpStream, ABC):
    url_base = "https://www.xledger.net/Flex/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        titles = [field['title'] for field in response.json().get('fields')]

        for row in response.json().get('rows'):
            yield dict(zip(titles, row))


class FinanceStream(ProjectSyncStream):
    primary_key = None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "112706017670337.json?t=APLF6qr6AIDformleE2ylIO4JVobFhEOOgwYrhOsczHeskNkyONT6VkddFwDUnNtkB6aPnxsSjB_Nxf5mh5vfdvyQ2P6tp2jzobDJTFkWVYR__NFcHG8I1eeKjKiTiVg9wed3_licUXTOAAskDomtJ10XVsZ4Y_wGgPGtdsh5HMltyLaBPtoqiq0soyOWhQ4WFOTCNjPb2MV_qRrEF7waksPdydnNxiP4gDYWHFTnjwTYrHg7L_YDJy5BtvfJpqRg6_G8SE38F1GXG5LxZZVcZXhBqyqorDssO77b02pYr202OZWW_gB7ZsuDyLAYgC20wNdwJL2NZrGTUKLs18v"


class StaffTrackStream(ProjectSyncStream):
    primary_key = None

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "112706021316758.json?t=APLF6mVnpZ6Nsgmrcemx1NkG5rszx064kMTXhY3bzGQ8Haw38LgMcJxB0wI3BvfPEgE6dzw6efnleXPBGzjeahQRzLfTMtqXt8Tg8auDvVK5-N16fFGJ3raqFm8Y2Bi887qWKaApkPW0fnnXsQ0Uo8AhDKZFURKVlvoxREn1WD1qgLOiXXEivsOR0B2fo_y-zQKDYBuNUi817W-_iBmeeQBcASW89q_QTfq6ABvweVDpBmlfYj85JMGfQbWmQsEf_AgaSqZHBD3ns2IMo3_703MYG_2SMqiGlYgCBdI2Zo-NtUaVZ1YjF6EgLJHbVsZ-aBc01i5lGdPliQev8mGZ"
