#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator
from requests.auth import HTTPBasicAuth

logger = logging.getLogger("airbyte")

# Basic full refresh stream


class AppfollowStream(HttpStream, ABC):

    url_base = "https://api.appfollow.io/"

    def __init__(self, ext_id: str, cid: str, **kwargs):
        super().__init__(**kwargs)
        self.ext_id = ext_id
        self.cid = cid

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Include common app and client parameters
        """
        return {"ext_id": self.ext_id, "cid": self.cid}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        yield response_json


class Ratings(AppfollowStream):
    """
    Ratings is a stream that pulls app ratings data from the Appfollow API.
    """

    primary_key = None

    def __init__(self, country: str, **kwargs):
        super().__init__(**kwargs)
        self.country = country

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["country"] = self.country
        return params

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "ratings"


# Source


class SourceAppfollow(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        A connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        logger.info("Checking Appfollow API connection...")
        try:
            ext_id = config["ext_id"]
            cid = config["cid"]
            api_secret = config["api_secret"]
            response = requests.get(
                f"https://api.appfollow.io/ratings?ext_id={ext_id}&cid={cid}", auth=HTTPBasicAuth(api_secret, api_secret)
            )
            if response.status_code == 200:
                return True, None
            else:
                return False, "Invalid Appfollow API credentials"
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Appfollow streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = BasicHttpAuthenticator(username=config["api_secret"], password=config["api_secret"])
        args = {"ext_id": config["ext_id"], "cid": config["cid"]}
        return [Ratings(authenticator=auth, country=config["country"], **args)]
