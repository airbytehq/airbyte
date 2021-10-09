#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

PAYSTACK_API_BASE_URL = "https://api.paystack.co/"

# Source
class SourcePaystack(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection by fetching customers

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            response = requests.get(
                f"{PAYSTACK_API_BASE_URL}/customer?page=1&perPage=1", 
                headers={"Authorization": f"Bearer {config['secret_key']}"},
                verify=True
            )
            response.raise_for_status()
        except Exception as e:
            msg = e
            if e.response.status_code == 401:
                msg = 'Connection to Paystack could not be authorized. Please check your secret key.'

            return False, msg

        response_json = response.json()
        if response_json['status'] == False:
            return False, 'Connection test failed due to error: ' + response_json['message']

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return []
