# temp file change
#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Tuple

import requests

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class SourceInstagramApi(YamlDeclarativeSource):
    url_base: str

    def __init__(self):
        super().__init__(path_to_yaml="manifest.yaml")
        self.url_base = resolve_manifest(source=self).record.data["manifest"]["definitions"]["base_requester"]["url_base"]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            headers = TokenAuthenticator(token=config["access_token"]).get_auth_header()
            response = requests.get(url=f"{self.url_base}/me", headers=headers)
            if not response.ok or not (ig_id := response.json().get("id")):
                raise Exception("unable to verify connection")
            logger.info(f"Verified account with {ig_id=}")
        except Exception as exc:
            error_msg = repr(exc)
            return False, error_msg
        return super().check_connection(logger, config)
