#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""

RAPID_API_HOST = "amazon-product-reviews-keywords.p.rapidapi.com"
BASE_URL = "https://" + RAPID_API_HOST


def get_params(config: Mapping[str, Any]) -> Mapping[str, Any]:
    params = {
        "asin": config["asin"],
        "country": config["country"],
        "variants": 1,
        "top": 0
    }
    if config.__contains__("filter_by_star") \
            and config["filter_by_star"] is not None:
        params["filter_by_star"] = config["filter_by_star"]
    return params


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "X-RapidAPI-Key": config["key"],
        "X-RapidAPI-Host": RAPID_API_HOST
    }


class rapidap_reviews(HttpStream):
    url_base = BASE_URL
    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config_param = config

    @property
    def http_method(self) -> str:
        return "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None
                        ) -> Mapping[str, Any]:
        return get_header(self.config_param)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return get_params(self.config_param)

    def path(self, **kwargs) -> str:
        return f"/product/reviews"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 200:
            yield from response.json().get("reviews")
        else:
            raise Exception([{"message": "Only AES decryption is implemented."}])


# Source
class SourceRapidap(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = BASE_URL + "/product/reviews"
        try:
            result = requests.get(url, params=get_params(config), headers=get_header(config))
            return True, None
        except Exception as e:
            if isinstance(e, StopIteration):
                logger.error(
                    "Could not check connection without data for Reviews stream. Please change value for replication start date field."
                )
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [rapidap_reviews(config=config)]
