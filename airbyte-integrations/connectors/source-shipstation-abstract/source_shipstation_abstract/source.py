#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
import base64

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from requests.auth import AuthBase
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    ShipstationAbstractStream,
    Users, 
    Carriers,
    # Fulfillments
    )


class BasicAuthenticator(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Basic {self.token}"
        return r




# Basic incremental stream
class IncrementalShipstationAbstractStream(ShipstationAbstractStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class SourceShipstationAbstract(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            api_key = config.get("api_key")
            api_secret = config.get("api_secret")
            url = Users().path()
            payload = {}
            response=requests.get(url, auth=(api_key,api_secret), params=payload,)
            json_response = response.json()
            contains_user_id = any('userId' in item for item in json_response)
            if contains_user_id:
                return True, None
            return False, "Unable to fetch data from Shipstation API"
        except Exception as error:
            return False, f"Unable to connect to Shipstation API with the provided credentials - {error}"
        



    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        api_key = config.get("api_key")
        api_secret = config.get("api_secret")
        auth_token = f"{api_key}:{api_secret}"
        base64_auth_token = base64.b64encode(auth_token.encode("utf-8")).decode("utf-8")

        auth = BasicAuthenticator(base64_auth_token)
        return [Carriers(authenticator=auth),
                Users(authenticator=auth),]