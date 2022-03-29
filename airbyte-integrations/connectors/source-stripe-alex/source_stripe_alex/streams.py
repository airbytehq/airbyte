from abc import ABC
import requests
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import Stream

# Basic full refresh stream
class StripeAlexStream(HttpStream, ABC):

    def __init__(self, *, url_base: str, primary_key: str, retry_factor: float, max_retries: int):
        super().__init__()
        self._primary_key = primary_key
        self._url_base = url_base
        self._retry_factor = retry_factor
        self._max_retries = max_retries

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        yield {}

    def url_base(self) -> str:
        return self._url_base

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return ''

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @primary_key.setter
    def set_primary_key(self, value):
        self._primary_key = value

    @property
    def retry_factor(self) -> float:
        return self._retry_factor

    @retry_factor.setter
    def set_retry_factor(self, value):
        self.retry_factor = value

    @property
    def max_retries(self) -> Union[int, None]:
        return self._max_retries

    @max_retries.setter
    def set_max_retries(self, value):
        self._max_retries = value


class Invoices(StripeAlexStream):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
