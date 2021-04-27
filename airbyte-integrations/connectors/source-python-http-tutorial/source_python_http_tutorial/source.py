"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests

from base_python import AbstractSource, HttpStream, Stream
from base_python.cdk.streams.auth.core import NoAuth
from base_python.cdk.streams.auth.token import TokenAuthenticator

from datetime import datetime


class ExchangeRates(HttpStream):
    def __init__(self, base: str, **kwargs):
        super().__init__()
        self.base = base

    url_base = "https://api.ratesapi.io/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        # The "/latest" path gives us the latest currency exchange rates
        return "latest"

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the base currency as a query param so we do that in this method
        return {'base': self.base}

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly,
        # so we just return a list containing the response
        return [response.json()]


class SourcePythonHttpTutorial(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        accepted_currencies = {"USD", "JPY", "BGN", "CZK", "DKK"}  # there are more currencies but let's assume these are the only allowed ones
        input_currency = config['base']
        if input_currency not in accepted_currencies:
            return False, f"Input currency {input_currency} is invalid. Please input one of the following currencies: {accepted_currencies}"
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API. It's only included for completeness
        # of the example, but if you don't need authentication, you don't need to pass an authenticator at all.
        # Other authenticators are available for API token-based auth and Oauth2.
        auth = NoAuth()
        return [ExchangeRates(authenticator=auth)]
