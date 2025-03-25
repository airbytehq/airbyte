#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


logger = logging.getLogger("airbyte")


class BasicApiTokenAuthenticator(TokenAuthenticator):
    """basic Authorization header"""

    def __init__(self, email: str, password: str):
        # for API token auth we need to add the suffix '/token' in the end of email value
        email_login = email + "/token"
        token = base64.b64encode(f"{email_login}:{password}".encode("utf-8"))
        super().__init__(token.decode("utf-8"), auth_method="Basic")


class SourceZendeskSupport(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> [TokenAuthenticator, BasicApiTokenAuthenticator]:
        # new authentication flow
        auth = config.get("credentials")
        if auth:
            if auth.get("credentials") == "oauth2.0":
                return TokenAuthenticator(token=config["credentials"]["access_token"])
            elif auth.get("credentials") == "api_token":
                return BasicApiTokenAuthenticator(config["credentials"]["email"], config["credentials"]["api_token"])
            else:
                raise AirbyteTracedException(
                    failure_type=FailureType.config_error,
                    message=f"Not implemented authorization method: {config['credentials']}",
                )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully,
        (False, error) otherwise.
        """
        http_client = HttpClient(
            name="user_settings",
            logger=self.logger,
            authenticator=self.get_authenticator(config),
        )
        try:
            _, response = http_client.send_request(
                http_method="GET",
                url=f"https://{config['subdomain']}.zendesk.com/api/v2/account/settings.json",
                request_kwargs={},
            )
        except Exception as e:
            return False, e

        active_features = [k for k, v in response.json().get("settings", {}).get("active_features", {}).items() if v]
        if "organization_access_enabled" not in active_features:
            return (
                False,
                "Please verify that the account linked to the API key has organization_access_enabled and try again."
                "For more information visit https://support.zendesk.com/hc/en-us/articles/4408821417114-About-the-Organizations-page#topic_n2f_23d_nqb.",
            )
        return True, None

    def check_enterprise_streams(self, declarative_streams: List[Stream]) -> List[Stream]:
        """Returns relevant a list of available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        enterprise_stream_names = ["ticket_forms", "account_attributes", "attribute_definitions"]
        enterprise_streams = [s for s in declarative_streams if s.name in enterprise_stream_names]

        all_streams = [s for s in declarative_streams if s.name not in enterprise_stream_names]

        # TicketForms, AccountAttributes and AttributeDefinitions streams are only available for Enterprise Plan users,
        # but Zendesk API does not provide a public API to get user's subscription plan.
        # That's why we try to read at least one record from one of these streams and expose all of them in case of success
        # or skip them otherwise
        try:
            ticket_forms_stream = next((s for s in enterprise_streams if s.name == "ticket_forms"))
            for stream_slice in ticket_forms_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                for _ in ticket_forms_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                    break
                all_streams.extend(enterprise_streams)
        except Exception as e:
            logger.warning(f"An exception occurred while trying to access TicketForms stream: {str(e)}. Skipping this stream.")
        return all_streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        declarative_streams = super().streams(config)
        return self.check_enterprise_streams(declarative_streams)
