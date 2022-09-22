#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Any, List, Mapping, Tuple

import requests
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
    UserSubscriptionStream,
)

# The Zendesk Subscription Plan gains complete access to all the streams
FULL_ACCESS_PLAN = "Enterprise"
FULL_ACCESS_ONLY_STREAMS = ["ticket_forms"]


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
        }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Returns relevant a list of available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = self.convert_config2stream_args(config)
        all_streams_mapping = {
            # sorted in alphabet order
            "group_membership": GroupMemberships(**args),
            "groups": Groups(**args),
            "macros": Macros(**args),
            "organizations": Organizations(**args),
            "satisfaction_ratings": SatisfactionRatings(**args),
            "sla_policies": SlaPolicies(**args),
            "tags": Tags(**args),
            "ticket_audits": TicketAudits(**args),
            "ticket_comments": TicketComments(**args),
            "ticket_fields": TicketFields(**args),
            "ticket_forms": TicketForms(**args),
            "ticket_metrics": TicketMetrics(**args),
            "ticket_metric_events": TicketMetricEvents(**args),
            "tickets": Tickets(**args),
            "users": Users(**args),
            "brands": Brands(**args),
            "custom_roles": CustomRoles(**args),
            "schedules": Schedules(**args),
        }
        # check the users Zendesk Subscription Plan
        subscription_plan = UserSubscriptionStream(**args).get_subscription_plan()
        if subscription_plan != FULL_ACCESS_PLAN:
            # only those the streams that are not listed in FULL_ACCESS_ONLY_STREAMS should be available
            return [stream_cls for stream_name, stream_cls in all_streams_mapping.items() if stream_name not in FULL_ACCESS_ONLY_STREAMS]
        else:
            # all streams should be available for user, otherwise
            return [stream_cls for stream_cls in all_streams_mapping.values()]
