#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.cac.checks.check_stream import CheckStream
from airbyte_cdk.sources.cac.configurable_connector import ConfigurableConnector
from airbyte_cdk.sources.cac.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.cac.extractors.jq import JqExtractor
from airbyte_cdk.sources.cac.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator
from airbyte_cdk.sources.cac.iterators.only_once import OnlyOnceIterator
from airbyte_cdk.sources.cac.requesters.http_requester import HttpMethod, HttpRequester
from airbyte_cdk.sources.cac.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.cac.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.cac.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.cac.requesters.paginators.offset_pagination import OffsetPagination
from airbyte_cdk.sources.cac.requesters.request_params.interpolated_request_parameter_provider import InterpolatedRequestParameterProvider
from airbyte_cdk.sources.cac.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.cac.schema.json_schema import JsonSchema
from airbyte_cdk.sources.cac.states.dict_state import DictState
from airbyte_cdk.sources.cac.states.no_state import NoState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

"""
class SendGridExtractor(Extractor):
    def __init__(self, data_field: Optional[str]):
        self.data_field = data_field

    def extract_records(self, response: requests.Response) -> List[Record]:
        decoded = response.json()
        if self.data_field:
            return decoded.get(self.data_field, [])
        else:
            return decoded
"""


class SendgridSource(ConfigurableConnector):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Define some shared constants
        authenticator = TokenAuthenticator(config["apikey"])
        limit = 5
        kwargs = {
            "url_base": "https://api.sendgrid.com/v3/",
            "http_method": HttpMethod.GET,  # This is a typed enum
            "authenticator": authenticator,
            "config": config,
        }
        metadata_paginator = NextPageUrlPaginator(
            interpolated_paginator=InterpolatedPaginator({"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}, config),
            kwargs=kwargs,
        )

        # Define the streams
        streams = [
            ConfigurableStream(
                name="lists",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/lists.json"),
                retriever=SimpleRetriever(
                    state=NoState(),
                    iterator=OnlyOnceIterator(),
                    requester=HttpRequester(
                        path=InterpolatedString("{{ next_page_token['next_page_url'] }}", "marketing/lists"),
                        request_parameters_provider=InterpolatedRequestParameterProvider({}, config),
                        kwargs=kwargs,
                    ),
                    paginator=metadata_paginator,
                    extractor=JqExtractor(".result[]"),
                ),
            ),
            ConfigurableStream(
                name="campaigns",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/campaigns.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path=InterpolatedString("{{ next_page_token['next_page_url'] }}", "marketing/campaigns"),
                        request_parameters_provider=InterpolatedRequestParameterProvider(kwargs=kwargs),  # No request parameters...
                        kwargs=kwargs,  # url_base can be passed directly or through kwargs
                    ),
                    extractor=JqExtractor(transform=".result[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            ConfigurableStream(
                name="contacts",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/contacts.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path="marketing/contacts",
                        request_parameters_provider=InterpolatedRequestParameterProvider(kwargs=kwargs),  # No request parameters...
                        kwargs=kwargs,  # url_base can be passed directly or through kwargs
                    ),
                    extractor=JqExtractor(transform=".result[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            ConfigurableStream(
                name="stats_automations",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/stats_automations.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path=InterpolatedString("{{ next_page_token['next_page_url'] }}", "marketing/stats/automations"),
                        # FIXME: would be nice to share the path across streams...
                        request_parameters_provider=InterpolatedRequestParameterProvider(kwargs=kwargs),  # No request parameters...
                        kwargs=kwargs,  # url_base can be passed directly or through kwargs
                    ),
                    extractor=JqExtractor(transform=".results[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            ConfigurableStream(
                name="segments",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/segments.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path="marketing/segments",
                        request_parameters_provider=InterpolatedRequestParameterProvider(kwargs=kwargs),  # No request parameters...
                        kwargs=kwargs,  # url_base can be passed directly or through kwargs
                    ),
                    extractor=JqExtractor(transform=".results[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            ConfigurableStream(
                name="bounces",
                primary_key="email",
                cursor_field=["created"],  # This stream has a cursor field
                schema=JsonSchema("./source_sendgrid/schemas/bounces.json"),
                retriever=SimpleRetriever(
                    state=DictState("created", "{{ last_record['created'] }}", state_type=int),
                    iterator=DatetimeIterator(
                        InterpolatedString("{{ stream_state['created'] }}", "{{ config['start_time'] }}"),
                        InterpolatedString("{{ today_utc() }}"),
                        step="1000d",
                        cursor_value=InterpolatedString("{{ stream_state['created'] }}"),
                        datetime_format="%Y-%m-%d",
                        config=config,
                    ),
                    requester=HttpRequester(
                        path="suppression/bounces",
                        request_parameters_provider=InterpolatedRequestParameterProvider(
                            # extract value from stream_state similar to how we're usually doing
                            request_parameters={
                                "start_time": "{{ stream_state['created'] }}",
                                # We can define specific functions callable from the interpolation
                                "end_time": "{{ utc_now() }}",
                            },
                            config=config,
                        ),
                        kwargs=kwargs,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=NoPagination(),
                ),
            ),
            ConfigurableStream(
                name="suppression_group_members",
                primary_key="group_id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/suppression_group_members.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path="asm/suppressions",
                        request_parameters_provider=InterpolatedRequestParameterProvider(
                            request_parameters={"offset": "{{ next_page_token['offset'] }}", "limit": limit},
                            config=config,
                        ),
                        kwargs=kwargs,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=OffsetPagination(limit),
                ),
            ),
        ]

        return streams

    # Define how to check the connection
    def connection_checker(self):
        return CheckStream(self)
