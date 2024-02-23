#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from datetime import datetime
from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_zendesk_support.streams import DATETIME_FORMAT, ZendeskConfigException

from .streams import (
    AccountAttributes,
    ArticleComments,
    ArticleCommentVotes,
    Articles,
    ArticleVotes,
    AttributeDefinitions,
    AuditLogs,
    Brands,
    CustomRoles,
    GroupMemberships,
    Groups,
    Macros,
    OrganizationFields,
    OrganizationMemberships,
    Organizations,
    PostComments,
    PostCommentVotes,
    Posts,
    PostVotes,
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
    TicketSkips,
    Topics,
    UserFields,
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
    def get_default_start_date(cls) -> str:
        """
        Gets the default start date for data retrieval.

        The default date is set to the current date and time in UTC minus 2 years.

        Returns:
            str: The default start date in 'YYYY-MM-DDTHH:mm:ss[Z]' format.

        Note:
            Start Date is a required request parameter for Zendesk Support API streams.
        """
        return pendulum.now(tz="UTC").subtract(years=2).format("YYYY-MM-DDTHH:mm:ss[Z]")

    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> [TokenAuthenticator, BasicApiTokenAuthenticator]:
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
                raise ZendeskConfigException(message=f"Not implemented authorization method: {config['credentials']}")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully,
        (False, error) otherwise.
        """
        auth = self.get_authenticator(config)
        try:
            datetime.strptime(config["start_date"], DATETIME_FORMAT)
            settings = UserSettingsStream(config["subdomain"], authenticator=auth, start_date=None).get_settings()
        except Exception as e:
            return False, e
        active_features = [k for k, v in settings.get("active_features", {}).items() if v]
        if "organization_access_enabled" not in active_features:
            return (
                False,
                "Please verify that the account linked to the API key has admin permissions and try again."
                "For more information visit https://support.zendesk.com/hc/en-us/articles/4408832171034-About-team-member-product-roles-and-access.",
            )
        return True, None

    @classmethod
    def convert_config2stream_args(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Convert input configs to parameters of the future streams
        This function is used by unit tests too
        """
        return {
            "subdomain": config["subdomain"],
            "start_date": config.get("start_date", cls.get_default_start_date()),
            "authenticator": cls.get_authenticator(config),
            "ignore_pagination": config.get("ignore_pagination", False),
        }

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Returns relevant a list of available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = self.convert_config2stream_args(config)
        streams = [
            Articles(**args),
            ArticleComments(**args),
            ArticleCommentVotes(**args),
            ArticleVotes(**args),
            AuditLogs(**args),
            GroupMemberships(**args),
            Groups(**args),
            Macros(**args),
            Organizations(**args),
            OrganizationFields(**args),
            OrganizationMemberships(**args),
            Posts(**args),
            PostComments(**args),
            PostCommentVotes(**args),
            PostVotes(**args),
            SatisfactionRatings(**args),
            SlaPolicies(**args),
            Tags(**args),
            TicketAudits(**args),
            TicketComments(**args),
            TicketFields(**args),
            TicketMetrics(**args),
            TicketMetricEvents(**args),
            TicketSkips(**args),
            Tickets(**args),
            Topics(**args),
            Users(**args),
            Brands(**args),
            CustomRoles(**args),
            Schedules(**args),
            UserFields(**args),
        ]
        ticket_forms_stream = TicketForms(**args)
        account_attributes = AccountAttributes(**args)
        attribute_definitions = AttributeDefinitions(**args)
        # TicketForms, AccountAttributes and AttributeDefinitions streams are only available for Enterprise Plan users,
        # but Zendesk API does not provide a public API to get user's subscription plan.
        # That's why we try to read at least one record from one of these streams and expose all of them in case of success
        # or skip them otherwise
        try:
            for stream_slice in ticket_forms_stream.stream_slices(sync_mode=SyncMode.full_refresh):
                for _ in ticket_forms_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                    streams.extend([ticket_forms_stream, account_attributes, attribute_definitions])
                    break
        except Exception as e:
            logger.warning(f"An exception occurred while trying to access TicketForms stream: {str(e)}. Skipping this stream.")
        return streams
