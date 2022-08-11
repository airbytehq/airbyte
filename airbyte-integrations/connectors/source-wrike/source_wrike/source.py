#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class WrikeStream(HttpStream, ABC):
    url_base = "https://app-us2.wrike.com/api/v4/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        resp = response.json()
        for task in resp['data']:
            yield task


class Tasks(WrikeStream):

    primary_key = "id"
    
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {"fields": "[customFields,parentIds,authorIds,responsibleIds,description,briefDescription,superTaskIds]"}

    def path(self, **kwargs) -> str:
        return "tasks"


class Customfields(WrikeStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "customfields"

# Source


class SourceWrike(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            headers = {
                "Accept": "application/json",
                "Authorization": "Bearer " + config["access_token"],
            }

            resp = requests.get(
                f"https://{config['wrike_instance']}/api/v4/version", headers=headers)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None

            error = resp.json()
            message = error.get("errorDescription") or error.get("error")
            return False, message
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        # Oauth2Authenticator is also available if you need oauth support
        auth = TokenAuthenticator(token=config["access_token"])
        return [Tasks(authenticator=auth), Customfields(authenticator=auth)]
