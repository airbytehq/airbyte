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
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level


from .streams import ZenhubWorkspace, ZenhubPipelines
from .utils import find_id_by_name, log

logging.basicConfig(level=logging.INFO)

# Source
class SourceZenhubGraphql(AbstractSource):
    
    @property
    def primary_key(self):
        return None
    
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
        
        # TODO remove the authenticator if not required.
        api_key = config["access_token"]  # Oauth2Authenticator is also available if you need oauth support
        workspace_name = config["workspace_name"]

        # Instantiate ZenhubWorkspace to get workspace IDs
        zenhub_workspace_stream = ZenhubWorkspace(api_key, workspace_name)
        workspace_data = next(zenhub_workspace_stream.read_records(sync_mode=SyncMode.full_refresh))
        log(Level.INFO, f"WorkspaceData: {workspace_data}")

        workspace_id = workspace_data['workspace_id']
        #log(Level.INFO, f"workspace_id: {workspace_id}")

        
        if not workspace_id:
            raise Exception(f"No workspace found with name: {workspace_name}")


        return [
                ZenhubWorkspace(api_key, workspace_name)
                ,ZenhubPipelines(api_key, workspace_id)
                ]