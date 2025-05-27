#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from http import HTTPStatus
from itertools import chain
from typing import Any, Generator, List, Mapping, Optional, Tuple

from requests import HTTPError

from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction
from source_hubspot.errors import HubspotInvalidAuth
from source_hubspot.streams import (
    API,
    BaseStream,
    CompaniesWebAnalytics,
    Contacts,
    ContactsWebAnalytics,
    CustomObject,
    DealsWebAnalytics,
    EngagementsCallsWebAnalytics,
    EngagementsEmailsWebAnalytics,
    EngagementsMeetingsWebAnalytics,
    EngagementsNotesWebAnalytics,
    EngagementsTasksWebAnalytics,
    GoalsWebAnalytics,
    LineItemsWebAnalytics,
    ProductsWebAnalytics,
    TicketsWebAnalytics,
    WebAnalyticsStream,
)


"""
https://github.com/airbytehq/oncall/issues/3800
we use start date 2006-01-01  as date of creation of Hubspot to retrieve all data if start date was not provided

"""
DEFAULT_START_DATE = "2006-06-01T00:00:00Z"
scopes = {
    "campaigns": {"crm.lists.read"},
    "companies": {"crm.objects.contacts.read", "crm.objects.companies.read"},
    "companies_property_history": {"crm.objects.companies.read"},
    "contact_lists": {"crm.lists.read"},
    "contacts": {"crm.objects.contacts.read"},
    "contacts_property_history": {"crm.objects.contacts.read"},
    "deal_pipelines": {"crm.objects.contacts.read"},
    "deal_splits": {"crm.objects.deals.read"},
    "deals": {"contacts", "crm.objects.deals.read"},
    "deals_property_history": {"crm.objects.deals.read"},
    "email_events": {"content"},
    "email_subscriptions": {"content"},
    "engagements": {"crm.objects.companies.read", "crm.objects.contacts.read", "crm.objects.deals.read", "tickets", "e-commerce"},
    "engagements_calls": {"crm.objects.contacts.read"},
    "engagements_emails": {"crm.objects.contacts.read", "sales-email-read"},
    "engagements_meetings": {"crm.objects.contacts.read"},
    "engagements_notes": {"crm.objects.contacts.read"},
    "engagements_tasks": {"crm.objects.contacts.read"},
    "marketing_emails": {"content"},
    "deals_archived": {"contacts", "crm.objects.deals.read"},
    "forms": {"forms"},
    "form_submissions": {"forms"},
    "goals": {"crm.objects.goals.read"},
    "leads": {"crm.objects.contacts.read", "crm.objects.companies.read", "crm.objects.leads.read"},
    "line_items": {"e-commerce", "crm.objects.line_items.read"},
    "owners": {"crm.objects.owners.read"},
    "owners_archived": {"crm.objects.owners.read"},
    "products": {"e-commerce"},
    "subscription_changes": {"content"},
    "ticket_pipelines": {
        "media_bridge.read",
        "tickets",
        "crm.schemas.custom.read",
        "e-commerce",
        "timeline",
        "contacts",
        "crm.schemas.contacts.read",
        "crm.objects.contacts.read",
        "crm.objects.contacts.write",
        "crm.objects.deals.read",
        "crm.schemas.quotes.read",
        "crm.objects.deals.write",
        "crm.objects.companies.read",
        "crm.schemas.companies.read",
        "crm.schemas.deals.read",
        "crm.schemas.line_items.read",
        "crm.objects.companies.write",
    },
    "tickets": {"tickets"},
    "workflows": {"automation"},
}


properties_scopes = {
    "companies_property_history": {"crm.schemas.companies.read"},
    "contacts_property_history": {"crm.schemas.contacts.read"},
    "deals_property_history": {"crm.schemas.deals.read"},
}


def scope_is_granted(stream: Stream, granted_scopes: List[str]) -> bool:
    """
    Set of required scopes. Users need to grant at least one of the scopes for the stream to be avaialble to them
    """
    granted_scopes = set(granted_scopes)
    if isinstance(stream, BaseStream):
        return stream.scope_is_granted(granted_scopes)
    else:
        # The default value is scopes for custom objects streams
        return len(scopes.get(stream.name, {"crm.schemas.custom.read", "crm.objects.custom.read"}).intersection(granted_scopes)) > 0


def properties_scope_is_granted(stream: Stream, granted_scopes: List[str]) -> bool:
    """
    Set of required scopes. Users need to grant at least one of the scopes for the stream to be avaialble to them
    """
    granted_scopes = set(granted_scopes)
    if isinstance(stream, BaseStream):
        return stream.properties_scope_is_granted()
    else:
        return not properties_scopes.get(stream.name, set()) - granted_scopes


class SourceHubspot(YamlDeclarativeSource):
    logger = logging.getLogger("airbyte")

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Check connection"""
        common_params = self.get_common_params(config=config)
        alive = True
        error_msg = None
        try:
            contacts = Contacts(**common_params)
            _ = contacts.properties
        except HTTPError as error:
            alive = False
            error_msg = repr(error)
            if error.response.status_code == HTTPStatus.BAD_REQUEST:
                response_json = error.response.json()
                error_msg = f"400 Bad Request: {response_json['message']}, please check if provided credentials are valid."
        except HubspotInvalidAuth as e:
            alive = False
            error_msg = repr(e)
        return alive, error_msg

    def get_granted_scopes(self, authenticator):
        try:
            access_token = authenticator.get_access_token()
            url = f"https://api.hubapi.com/oauth/v1/access-tokens/{access_token}"
            error_resolution = ErrorResolution(
                ResponseAction.RETRY, FailureType.transient_error, "Internal error attempting to get scopes."
            )
            error_mapping = {500: error_resolution, 502: error_resolution, 504: error_resolution}
            http_client = HttpClient(
                name="get hubspot granted scopes client",
                logger=self.logger,
                error_handler=HttpStatusErrorHandler(logger=self.logger, error_mapping=error_mapping),
            )
            request, response = http_client.send_request("get", url, request_kwargs={})
            response.raise_for_status()
            response_json = response.json()
            granted_scopes = response_json["scopes"]
            return granted_scopes
        except Exception as e:
            return False, repr(e)

    @staticmethod
    def get_api(config: Mapping[str, Any]) -> API:
        credentials = config.get("credentials", {})
        return API(credentials=credentials)

    def get_common_params(self, config) -> Mapping[str, Any]:
        start_date = config.get("start_date", DEFAULT_START_DATE)
        credentials = config["credentials"]
        api = self.get_api(config=config)
        # Additional configuration is necessary for testing certain streams due to their specific restrictions.
        acceptance_test_config = config.get("acceptance_test_config", {})
        return dict(api=api, start_date=start_date, credentials=credentials, acceptance_test_config=acceptance_test_config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = config.get("credentials", {})
        common_params = self.get_common_params(config=config)
        # Temporarily using `ConcurrentDeclarativeSource.streams()` to validate granted scopes.
        streams = super().streams(config=config)

        enable_experimental_streams = "enable_experimental_streams" in config and config["enable_experimental_streams"]

        if enable_experimental_streams:
            streams.extend(
                [
                    ContactsWebAnalytics(**common_params),
                    CompaniesWebAnalytics(**common_params),
                    DealsWebAnalytics(**common_params),
                    TicketsWebAnalytics(**common_params),
                    EngagementsCallsWebAnalytics(**common_params),
                    EngagementsEmailsWebAnalytics(**common_params),
                    EngagementsMeetingsWebAnalytics(**common_params),
                    EngagementsNotesWebAnalytics(**common_params),
                    EngagementsTasksWebAnalytics(**common_params),
                    GoalsWebAnalytics(**common_params),
                    LineItemsWebAnalytics(**common_params),
                    ProductsWebAnalytics(**common_params),
                ]
            )

        api = API(credentials=credentials)
        if api.is_oauth2():
            authenticator = api.get_authenticator()
            granted_scopes = self.get_granted_scopes(authenticator)
            self.logger.info(f"The following scopes were granted: {granted_scopes}")

            available_streams = [stream for stream in streams if scope_is_granted(stream, granted_scopes)]
            unavailable_streams = [stream for stream in streams if not scope_is_granted(stream, granted_scopes)]
            self.logger.info(f"The following streams are unavailable: {[s.name for s in unavailable_streams]}")
            partially_available_streams = [stream for stream in streams if not properties_scope_is_granted(stream, granted_scopes)]
            required_scoped = set(
                chain(
                    *[
                        properties_scopes.get(x.name, set()) if isinstance(x, DeclarativeStream) else x.properties_scopes
                        for x in partially_available_streams
                    ]
                )
            )
            self.logger.info(
                f"The following streams are partially available: {[s.name for s in partially_available_streams]}, "
                f"add the following scopes to download all available data: {required_scoped}"
            )
        else:
            self.logger.info("No scopes to grant when authenticating with API key.")
            available_streams = streams

        custom_object_streams = list(self.get_custom_object_streams(api=api, common_params=common_params))

        if enable_experimental_streams:
            custom_objects_web_analytics_streams = self.get_web_analytics_custom_objects_stream(
                custom_object_stream_instances=custom_object_streams,
                common_params=common_params,
            )
            available_streams.extend(custom_objects_web_analytics_streams)

        return available_streams

    def get_custom_object_streams(self, api: API, common_params: Mapping[str, Any]):
        for entity, fully_qualified_name, schema, custom_properties in api.get_custom_objects_metadata():
            yield CustomObject(
                entity=entity,
                schema=schema,
                fully_qualified_name=fully_qualified_name,
                custom_properties=custom_properties,
                **common_params,
            )

    def get_web_analytics_custom_objects_stream(
        self, custom_object_stream_instances: List[CustomObject], common_params: Any
    ) -> Generator[WebAnalyticsStream, None, None]:
        for custom_object_stream_instance in custom_object_stream_instances:

            def __init__(self, **kwargs: Any):
                parent = custom_object_stream_instance.__class__(
                    entity=custom_object_stream_instance.entity,
                    schema=custom_object_stream_instance.schema,
                    fully_qualified_name=custom_object_stream_instance.fully_qualified_name,
                    custom_properties=custom_object_stream_instance.custom_properties,
                    **common_params,
                )
                super(self.__class__, self).__init__(parent=parent, **kwargs)

            custom_web_analytics_stream_class = type(
                f"{custom_object_stream_instance.name.capitalize()}WebAnalytics", (WebAnalyticsStream,), {"__init__": __init__}
            )

            yield custom_web_analytics_stream_class(**common_params)
