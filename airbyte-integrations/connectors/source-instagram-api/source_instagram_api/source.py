#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Tuple

import requests
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

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
class SourceInstagramApi(YamlDeclarativeSource):

    def __init__(self):
        super().__init__(path_to_yaml="manifest.yaml")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            response = requests.get(
                url="https://graph.instagram.com/v22.0/me",
                headers=TokenAuthenticator(token=config["access_token"]).get_auth_header()
            )
            if not response.ok or not (ig_id := response.json().get("id")):
                raise Exception("unable to verify connection")

            logger.info(f"Verified account with {ig_id=}")
        except Exception as exc:
            error_msg = repr(exc)
            return False, error_msg
        return super().check_connection(logger, config)
