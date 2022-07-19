#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

logger = logging.getLogger("airbyte")


class SourceDockerhub(AbstractSource):
    jwt = None

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        username = config["docker_username"]

        # get JWT
        jwt_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull"
        response = requests.get(jwt_url)
        self.jwt = response.json()["token"]

        # check that jwt is valid and that username is valid
        url = f"https://hub.docker.com/v2/repositories/{username}/"
        try:
            response = requests.get(url, headers={"Authorization": self.jwt})
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.info(str(e))
                return False, "Invalid JWT received, check if auth.docker.io changed API"
            elif e.response.status_code == 404:
                logger.info(str(e))
                return False, f"User '{username}' not found, check if hub.docker.com/u/{username} exists"
            else:
                logger.info(str(e))
                return False, f"Error getting basic user info for Docker user '{username}', unexpected error"
        json_response = response.json()
        repocount = json_response["count"]
        logger.info(f"Connection check for Docker user '{username}' successful: {repocount} repos found")
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [DockerHub(jwt=self.jwt, config=config)]


class DockerHub(HttpStream):
    url_base = "https://hub.docker.com/v2"

    # Set this as a noop.
    primary_key = None

    def __init__(self, jwt: str, config: Mapping[str, Any], **kwargs):
        super().__init__()
        # Here's where we set the variable from our input to pass it down to the source.
        self.jwt = jwt
        self.docker_username = config["docker_username"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        if decoded_response["next"] is None:
            return None
        else:
            para = urlparse(decoded_response["next"]).query
            return "?" + para

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = ""
    ) -> str:
        return f"/v2/repositories/{self.docker_username}/" + str(next_page_token or "")

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": self.jwt}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        for repository in response.json().get("results"):
            yield repository
