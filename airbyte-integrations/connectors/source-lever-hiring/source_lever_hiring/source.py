#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator, Oauth2Authenticator

from .streams import Applications, Interviews, Notes, Offers, Opportunities, Referrals, Users


def _auth_from_config(config):
    try:
        if config["credentials"]["auth_type"] == "Api Key":
            return BasicHttpAuthenticator(username=config["credentials"]["api_key"], password=None, auth_method="Basic")
        elif config["credentials"]["auth_type"] == "Client":
            return Oauth2Authenticator(
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
                token_refresh_endpoint=f"{SourceLeverHiring.URL_MAP_ACCORDING_ENVIRONMENT[config['environment']]['login']}oauth/token",
            )
        else:
            print("Auth type was not configured properly")
            return None
    except Exception as e:
        print(f"{e.__class__} occurred, there's an issue with credentials in your config")
        raise e


class SourceLeverHiring(AbstractSource):
    URL_MAP_ACCORDING_ENVIRONMENT = {
        "Sandbox": {
            "login": "https://sandbox-lever.auth0.com/",
            "api": "https://api.sandbox.lever.co/",
        },
        "Production": {
            "login": "https://auth.lever.co/",
            "api": "https://api.lever.co/",
        },
    }

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        authenticator = _auth_from_config(config)
        _ = authenticator.get_auth_header()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        authenticator = _auth_from_config(config)
        full_refresh_params = {
            "authenticator": authenticator,
            "base_url": self.URL_MAP_ACCORDING_ENVIRONMENT[config["environment"]]["api"],
        }
        stream_params_with_start_date = {
            **full_refresh_params,
            "start_date": config["start_date"],
        }
        return [
            Applications(**stream_params_with_start_date),
            Interviews(**stream_params_with_start_date),
            Notes(**stream_params_with_start_date),
            Offers(**stream_params_with_start_date),
            Opportunities(**stream_params_with_start_date),
            Referrals(**stream_params_with_start_date),
            Users(**full_refresh_params),
        ]
