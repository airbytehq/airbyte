#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from source_strava.streams import Activities, AthleteStats


# Source
class SourceStrava(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = self.get_oauth(config)
            _ = auth.get_auth_header()
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = self.get_oauth(config)
        return [
            AthleteStats(authenticator=auth, athlete_id=config["athlete_id"]),
            Activities(authenticator=auth, after=config["start_date"]),
        ]

    def get_oauth(self, config):
        return Oauth2Authenticator(
            token_refresh_endpoint="https://www.strava.com/oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
            scopes=["read_all", "activity:read_all"],
        )
