#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class AttioStream(HttpStream, ABC):
    url_base = "https://api.attio.com/v2/"

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Authentication headers will overwrite any overlapping headers returned from this method.
        Authentication headers are handled by an HttpAuthenticator.
        """
        return {"Content-Type": "application/json"}

    headers = request_headers


class WorkspaceMembers(AttioStream):
    primary_key = ["workspace_id", "workspace_member_id"]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "workspace_members"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        members = response.json()["data"]
        for member in members:
            member["workspace_id"] = member["id"]["workspace_id"]
            member["workspace_member_id"] = member["id"]["workspace_member_id"]
            del member["id"]
        return members

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination so we return None to indicate no more pages
        return None


# Source
class SourceAttio(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            response = requests.get(
                "https://api.attio.com/v2/self",
                headers={"Authorization": f"Bearer {config['access_token']}", "Content-Type": "application/json"},
            )
            response.raise_for_status()
            try:
                assert response.json()["active"] == True
            except Exception as e:
                print(e)
                raise Exception("Connection is inactive")
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        auth = TokenAuthenticator(config["access_token"])  # TODO support oauth with Oauth2Authenticator

        return [WorkspaceMembers(auth)]
