#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .full_refresh_streams import (
    Hardware,
    Companies,
    Locations,
    Accessories,
    Consumables,
    Components,
    Users,
    StatusLabels,
    Models,
    Licenses,
    Categories,
    Manufacturers,
    Maintenances,
    Departments,
)
from .incremental_streams import Events

"""
This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""

# Source
class SourceSnipeit(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        token = config.get("access_token", None)
        if token is None:
            return False, "You need to provide an Access Token! Check config and try again."
        elif token == "":
            return False, "Token cannot be an empty string! Check config and try again."
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        access_jwt = config.get("access_token")
        auth = TokenAuthenticator(token=access_jwt)  # Oauth2Authenticator is also available if you need oauth support
        return [
            Accessories(authenticator=auth, config=config),
            Categories(authenticator=auth, config=config),
            Companies(authenticator=auth, config=config),
            Components(authenticator=auth, config=config),
            Consumables(authenticator=auth, config=config),
            Departments(authenticator=auth, config=config),
            Events(authenticator=auth, config=config),
            Hardware(authenticator=auth, config=config),
            Licenses(authenticator=auth, config=config),
            Locations(authenticator=auth, config=config),
            Maintenances(authenticator=auth, config=config),
            Manufacturers(authenticator=auth, config=config),
            Models(authenticator=auth, config=config),
            StatusLabels(authenticator=auth, config=config),
            Users(authenticator=auth, config=config),
        ]
