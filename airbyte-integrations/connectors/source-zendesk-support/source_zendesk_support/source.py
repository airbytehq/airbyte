#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    GroupMemberships,
    Groups,
    Macros,
    Organizations,
    SatisfactionRatings,
    SlaPolicies,
    SourceZendeskException,
    Tags,
    TicketAudits,
    TicketComments,
    TicketFields,
    TicketForms,
    TicketMetrics,
    Tickets,
    Users,
    UserSettingsStream,
)


class BasicApiTokenAuthenticator(TokenAuthenticator):
    """basic Authorization header"""

    def __init__(self, email: str, password: str):
        # for API token auth we need to add the suffix '/token' in the end of email value
        email_login = email + "/token"
        token = base64.b64encode(f"{email_login}:{password}".encode("utf-8"))
        super().__init__(token.decode("utf-8"), auth_method="Basic")


class SourceZendeskSupport(AbstractSource):
    """Source Zendesk Support fetch data from Zendesk CRM that builds customer
    support and sales software which aims for quick implementation and adaptation at scale.
    """

    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> BasicApiTokenAuthenticator:
        if config["auth_method"].get("email") and config["auth_method"].get("api_token"):
            return BasicApiTokenAuthenticator(config["auth_method"]["email"], config["auth_method"]["api_token"])
        raise SourceZendeskException(f"Not implemented authorization method: {config['auth_method']}")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully,
        (False, error) otherwise.
        """
        auth = self.get_authenticator(config)
        settings = None
        try:
            settings = UserSettingsStream(config["subdomain"], authenticator=auth).get_settings()
        except requests.exceptions.RequestException as e:
            return False, e

        active_features = [k for k, v in settings.get("active_features", {}).items() if v]
        logger.info("available features: %s" % active_features)
        if "organization_access_enabled" not in active_features:
            return False, "Organization access is not enabled. Please check admin permission of the current account"
        return True, None

    @classmethod
    def convert_config2stream_args(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Convert input configs to parameters of the future streams
        This function is used by unit tests too
        """
        return {
            "subdomain": config["subdomain"],
            "start_date": config["start_date"],
            "authenticator": cls.get_authenticator(config),
        }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Returns relevant a list of available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = self.convert_config2stream_args(config)
        # sorted in alphabet order
        return [
            GroupMemberships(**args),
            Groups(**args),
            Macros(**args),
            Organizations(**args),
            SatisfactionRatings(**args),
            SlaPolicies(**args),
            Tags(**args),
            TicketAudits(**args),
            TicketComments(**args),
            TicketFields(**args),
            TicketForms(**args),
            TicketMetrics(**args),
            Tickets(**args),
            Users(**args),
        ]
