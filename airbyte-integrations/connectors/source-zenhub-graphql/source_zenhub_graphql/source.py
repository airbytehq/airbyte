#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import logging

import requests
import json, os
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import ZenhubWorkspace

logging.basicConfig(level=logging.INFO)

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
    
    def _get_workspace(self, config):
        try:
            #Get Ids
            ws_repo_ids = ZenhubWorkspace(
                api_key=config["access_token"]
                , workspace_name=config["workspace_name"]
            ) 
            next(ws_repo_ids.read_records(sync_mode= SyncMode.full_refresh))
            
            return True, None
        except Exception as error:
            return False, str(error)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            ws_query_body = ZenhubWorkspace(
                api_key=config["access_token"]
                , workspace_name=config["workspace_name"]
                )
            #repsonse has the actual data because we are using sgqlc HTTPEndpoint method.
            next(ws_query_body.read_records(sync_mode= SyncMode.full_refresh))
            return True, None
        except Exception as error:
            return False, str(error)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        api_key = config["access_token"]  # Oauth2Authenticator is also available if you need oauth support
        workspace_name = config["workspace_name"]
        return [ZenhubWorkspace(api_key, workspace_name)]