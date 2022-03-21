#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

import pdb
import requests
from requests.auth import HTTPBasicAuth
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from . import state_code_list

class Helpers(object):
    @staticmethod
    def get_states(state_code: str, api_key: str):

        url = f"https://api.collectapi.com/gasPrice/stateUsaPrice?state={state_code}"
        headers = {
            'content-type': "application/json",
            'authorization': f"{api_key}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            print(response.status_code)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key")
            elif e.response.status_code == 404:
                raise Exception(f"State code, {state_code} not found")
            else:
                raise Exception(f"Error getting data on {state_code}: {e}")
        json_response = response.json()
        return json_response
    