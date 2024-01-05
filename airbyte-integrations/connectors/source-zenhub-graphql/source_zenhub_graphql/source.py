#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import json, os
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import ZenhubWorkspace


"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Source
class SourceZenhubGraphql(AbstractSource):
    
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        ws_query_body = ZenhubWorkspace(
            api_key=config["access_token"]
            , workspace_name=config["workspace_name"]
            )
        
        #repsonse has the actual data because we are using sgqlc HTTPEndpoint method.
        #TODO: CHeck if SGQLC method is better than HttpStream. I was getting the headers error
        response, status_code = ws_query_body.fetch_data()
        
        if status_code == 200:
        #if response.status_code == 200:
            result = {"status": "SUCCEEDED"}
        elif status_code == 403:
        #elif response.status_code == 403:
            # HTTP code 403 means authorization failed so the API key is incorrect
            result = {"status": "FAILED", "message": "API Key is incorrect."}
        else:
            result = {"status": "FAILED", "message": "Input configuration is incorrect. Please verify your valid config file."}

        output_message = {"type": "CONNECTION_STATUS", "connectionStatus": result}
        print(json.dumps(output_message))

        #return True, None    
        return status_code == 200, None
    

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        return [Customers(authenticator=auth), Employees(authenticator=auth)]