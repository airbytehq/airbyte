#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from urllib.parse import urlparse, parse_qsl


class WoocommerceSubscriptionStream(HttpStream, ABC):

    def __init__(self, config):
        super().__init__()
        print(config)
        self.shop = config.get('shop', '')
        self.consumer_key = config.get('consumer_key', '')
        self.consumer_secret = config.get('consumer_secret', '')
        self.page_offset = 1
        self.batch_size = 100

    @property
    def url_base(self) -> str:
        return f"https://{self.shop}/wp-json/wc/v3/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_url = response.links.get("next", {}).get("url", "")
        if next_url != "":
            return dict(parse_qsl(urlparse(next_url).query))
        else:
            return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        default_params = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
            "per_page": self.batch_size,
            "page": self.page_offset,
        }
        if next_page_token:
            default_params.update(next_page_token)

        return default_params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Subscriptions(WoocommerceSubscriptionStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "subscriptions"


class SourceWoocommerceSubscription(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Subscriptions(config=config)]
