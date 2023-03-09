#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_zendesk_support.streams import SourceZendeskException

from .streams import (
    Brands,
    CustomRoles,
    GroupMemberships,
    Groups,
    Macros,
    Organizations,
    SatisfactionRatings,
    Schedules,
    SlaPolicies,
    Tags,
    TicketAudits,
    TicketComments,
    TicketFields,
    TicketForms,
    TicketMetricEvents,
    TicketMetrics,
    Tickets,
    Users,
    UserSettingsStream,
)

logger = logging.getLogger("airbyte")


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

        # old authentication flow support
        auth_old = config.get("auth_method")
        if auth_old:
            if auth_old.get("auth_method") == "api_token":
                return BasicApiTokenAuthenticator(config["auth_method"]["email"], config["auth_method"]["api_token"])
        # new authentication flow
        auth = config.get("credentials")
        if auth:
            if auth.get("credentials") == "oauth2.0":
                return TokenAuthenticator(token=config["credentials"]["access_token"])
            elif auth.get("credentials") == "api_token":
                return BasicApiTokenAuthenticator(config["credentials"]["email"], config["credentials"]["api_token"])
            else:
                raise SourceZendeskException(f"Not implemented authorization method: {config['credentials']}")

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
            settings = UserSettingsStream(config["subdomain"], authenticator=auth, start_date=None).get_settings()
        except requests.exceptions.RequestException as e:
            return False, e

        active_features = [k for k, v in settings.get("active_features", {}).items() if v]
        # logger.info("available features: %s" % active_features)
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
            "ignore_pagination": config.get("ignore_pagination", False),
        }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Returns relevant a list of available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = self.convert_config2stream_args(config)
        streams = [
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
            TicketMetrics(**args),
            TicketMetricEvents(**args),
            Tickets(**args),
            Users(**args),
            Brands(**args),
            CustomRoles(**args),
            Schedules(**args),
        ]
        ticket_forms_stream = TicketForms(**args)
        # TicketForms stream is only available for Enterprise Plan users but Zendesk API does not provide
        # a public API to get user's subscription plan. That's why we try to read at least one record and expose this stream
        # in case of success or skip it otherwise
        try:
            for stream_slice in ticket_forms_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                for _ in ticket_forms_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                    streams.append(ticket_forms_stream)
                    break
        except Exception as e:
            logger.warning(f"An exception occurred while trying to access TicketForms stream: {str(e)}. Skipping this stream.")
        return streams
