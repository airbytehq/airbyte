#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth.token import BasicHttpAuthenticator

from .streams import Contacts, Credits, Invoices


# Source
class SourceQuaderno(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Validate that the user-provided config can be used to connect to the underlying API.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]:   (True, None) if the input config can be used to connect to the API successfully,
                                    (False, error) otherwise.
        """
        response = requests.get("https://quadernoapp.com/api/authorization", auth=(config['api_key'], 'x'))
        if response.status_code == requests.codes.OK:
            if response.json()['identity']['href'] == f"https://{config['account_name']}.quadernoapp.com/api/":
                logger.debug("Connection to Quaderno was successful.")
                return True, None
            else:
                logger.info("Connection to Quaderno was unsuccessful. The API Key is not authorized for the account.")
                return False, "The API Key is not authorized for the account."
        else:
            logger.info(f"Connection to Quaderno was unsuccessful with status code {response.status_code}.")
            return (
                False,
                f"Authorization failed with status code {response.status_code}. "
                f"Error message: {response.json()['error']}"
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Generate the streams for this source.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = BasicHttpAuthenticator(username=config["api_key"], password="x")
        streams = [
            Contacts(authenticator=auth, config=config),
            Credits(authenticator=auth, config=config),
            Invoices(authenticator=auth, config=config),
        ]
        return streams
