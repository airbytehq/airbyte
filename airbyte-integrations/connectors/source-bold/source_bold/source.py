from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_bold.streams import Customers, Products, Categories


class SourceBold(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Check connection against user provided connection config by establishing connection with source.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None
        token = TokenAuthenticator(config.get("access_token"))

        try:
            Customers(config=config, authenticator=token)
            ok = True
        except Exception as e:
            error_msg = repr(e)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        token = TokenAuthenticator(config.get("access_token"))
        return [
            Customers(config=config, authenticator=token),
            Products(config=config, authenticator=token),
            Categories(config=config, authenticator=token),
        ]
