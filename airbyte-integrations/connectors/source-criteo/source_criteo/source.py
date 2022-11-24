#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, List, Mapping, Optional, Tuple
from urllib.parse import urlparse

import jsonschema
import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from .authenticator import CriteoAuthenticator
from source_criteo.streams import (
    Analytics
)


# Source
class SourceCriteo(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        pendulum.parse(config["start_date"])
        end_date = config.get("end_date")
        if end_date:
            pendulum.parse(end_date)
        config["end_date"] = end_date or pendulum.now().to_datetime_string().replace(' ', 'T') + 'Z'

        config["advertiserIds"] = config.get("advertiserIds")
        config["dimensions"] = config.get("dimensions")
        config["metrics"] = config.get("metrics")
        return config

    def get_stream_kwargs(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "advertiserIds": config["advertiserIds"],
            "start_date": config["start_date"],
            "end_date": config["end_date"],
            "authenticator": self.get_authenticator(config),
            "dimensions": config["dimensions"],
            "metrics": config["metrics"]
        }

    def get_authenticator(self, config):
        authorization = config["authorization"]
        auth_type = authorization["auth_type"]

        if auth_type == "Client":
            return CriteoAuthenticator(
                {'client_secret': authorization["client_secret"],
                 'client_id': authorization["client_id"],
                 'grant_type': "client_credentials"}
            )

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            config = self._validate_and_transform(config)

            authenticator = self.get_authenticator(config)

            if (authenticator.get_access_token()):
                return True, None
        except Exception as error:
            return (
                False,
                f"Unable to connect to Criteo API with the provided credentials - {repr(error)}",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = self._validate_and_transform(config)
        stream_config = self.get_stream_kwargs(config)

        streams = [Analytics(**stream_config)]

        return streams
