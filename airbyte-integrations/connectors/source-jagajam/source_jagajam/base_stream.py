#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import sys
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import backoff
import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests import exceptions

logger = logging.getLogger("airbyte")

TRANSIENT_EXCEPTIONS = (
    DefaultBackoffException,
    exceptions.ConnectTimeout,
    exceptions.ReadTimeout,
    exceptions.ConnectionError,
    exceptions.ChunkedEncodingError,
)


class JagajamStream(HttpStream, ABC):
    retry_factor: int = 2
    url_base = "https://new.jagajam.com/v3/"
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)

    def __init__(self, auth_token: str, client_name: str = None, product_name: str = None, custom_constants: Mapping[str, Any] = {}):
        HttpStream.__init__(self, authenticator=None)
        self.auth_token = auth_token
        self.client_name = client_name
        self.product_name = product_name
        self.custom_constants = custom_constants

    def _send_request(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        def default_backoff_handler(max_tries: Optional[int], factor: float, **kwargs):
            def log_retry_attempt(details):
                _, exc, _ = sys.exc_info()
                if exc.response:
                    logger.info(
                        f"Status code: {exc.response.status_code}, Response Content: {exc.response.content}")
                logger.info(
                    f"Caught retryable error '{str(exc)}' after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
                )

            def should_give_up(exc):
                give_up = not self.should_retry(exc.response)
                if give_up:
                    logger.info(
                        f"Giving up for returned HTTP status: {exc.response.status_code}")
                return give_up

            return backoff.on_exception(
                backoff.expo,
                TRANSIENT_EXCEPTIONS,
                jitter=None,
                on_backoff=log_retry_attempt,
                giveup=should_give_up,
                max_tries=max_tries,
                factor=factor,
                **kwargs,
            )
        max_tries = self.max_retries
        if max_tries is not None:
            max_tries = max(0, max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(
            max_tries=max_tries)(self._send)
        backoff_handler = default_backoff_handler(
            max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(request, request_kwargs)

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        return response.json()['meta']['message']

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def add_extra_properties_to_schema(self, schema):
        extra_properties = ["__productName",
                            "__clientName", *self.custom_constants.keys()]
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        return self.add_extra_properties_to_schema(schema)

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.product_name,
            "__clientName": self.client_name,
            **self.custom_constants
        }
        return {**record, **constants}

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"token": self.auth_token}

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Host": "new.jagajam.com",
            **super().request_headers(stream_state, stream_slice, next_page_token),
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from map(self.add_constants_to_record, response.json()['data'])

    def should_retry(self, response: requests.Response) -> bool:
        meta_status_code = response.json()['meta']['code']
        should_retry_on_meta = meta_status_code in [
            429, 408] or 500 <= meta_status_code < 600
        should_retry = should_retry_on_meta or super().should_retry(response)
        return should_retry
