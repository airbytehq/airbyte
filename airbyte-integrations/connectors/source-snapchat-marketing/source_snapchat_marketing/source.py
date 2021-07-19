#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, Oauth2Authenticator

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class SnapchatMarketingStream(HttpStream, ABC):
    # TODO: Fill in the url base. Required.
    url_base = "https://example-api.com/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}


class SnapchatAdsOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl -X POST https://accounts.snapchat.com/login/oauth2/access_token \
      -d "refresh_token={refresh_token}" \
      -d "client_id={client_id}" \
      -d "client_secret={client_secret}"  \
      -d "grant_type=refresh_token"  \
    """

    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint='https://accounts.snapchat.com/login/oauth2/access_token',
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        response_json = None
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint,
                                        data=self.get_refresh_request_body())
            response_json = response.json()
            response.raise_for_status()
            return response_json["access_token"], response_json["expires_in"]
        except requests.exceptions.RequestException as e:
            if response_json and 'error' in response_json:
                raise Exception("Error refreshing access token. Error: {}; Error details: {}; Exception: {}".format(
                    response_json['error'], response_json['error_description'], e)) from e

            raise Exception(f"Error refreshing access token: {e}") from e


# Source
class SourceSnapchatMarketing(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            auth = SnapchatAdsOauth2Authenticator(config)

            token = auth.get_access_token()

            url = 'https://adsapi.snapchat.com/v1/me'

            session = requests.get(url, headers={"Authorization": "Bearer {}".format(token)})
            session.raise_for_status()
            return True, None

        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = SnapchatAdsOauth2Authenticator(config)

        return []
