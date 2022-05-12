#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from functools import partial
from typing import Any, List, Mapping

from airbyte_cdk.sources.cac import create_partial
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


class SendgridSource(ConfigurableConnector):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Define some shared constants
        authenticator = TokenAuthenticator(config["apikey"])
        limit = 50

        metadata_paginator = NextPageUrlPaginator(
            interpolated_paginator=InterpolatedPaginator({"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}, config),
        )
        offset_request_parameters = {"offset": "{{ next_page_token['offset'] }}", "limit": limit}
        offset_pagination_request_parameters = InterpolatedRequestParameterProvider(
            request_parameters=offset_request_parameters,
            config=config,
        )
        cursor_request_parameters = {
            "start_time": "{{ stream_state['created'] }}",
            # We can define specific functions callable from the interpolation
            "end_time": "{{ utc_now() }}",
        }

        datetime_iterator = DatetimeIterator(
            InterpolatedString("{{ stream_state['created'] }}", "{{ config['start_time'] }}"),
            InterpolatedString("{{ today_utc() }}"),
            step="1000d",
            cursor_value=InterpolatedString("{{ stream_state['created'] }}"),
            datetime_format="%Y-%m-%d",
            config=config,
        )
        cursor_state = DictState("created", "{{ last_record['created'] }}", state_type=int)

        next_page_url_from_token_partial = partial(InterpolatedString, string="{{ next_page_token['next_page_url'] }}")

        simple_retriever = partial(SimpleRetriever, config=config)
        request_parameters_provider = partial(InterpolatedRequestParameterProvider, config=config)
        configurable_stream = partial(ConfigurableStream, config=config)
        new_configurable_stream = create_partial.create(ConfigurableStream, config=config)
        http_requester = partial(
            HttpRequester, url_base="https://api.sendgrid.com/v3/", config=config, http_method=HttpMethod.GET, authenticator=authenticator
        )

        # Define the streams
        streams = [
            new_configurable_stream(
                primary_key="id",
                cursor_field=[],
                schema=create_partial.create(JsonSchema, file_path="./source_sendgrid/schemas/{{kwargs['name']}}.json"),
                retriever=simple_retriever(
                    state=NoState(),
                    iterator=OnlyOnceIterator(),
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/lists"),
                        request_parameters_provider=request_parameters_provider(),
                    ),
                    paginator=metadata_paginator,
                    extractor=JqExtractor(".result[]"),
                ),
                kwargs={"name": "lists"},
            ),
            configurable_stream(
                name="campaigns",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/campaigns.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/campaigns"),
                        request_parameters_provider=request_parameters_provider(),  # No request parameters...
                    ),
                    extractor=JqExtractor(transform=".result[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="contacts",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/contacts.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/contacts",
                        request_parameters_provider=request_parameters_provider(),  # No request parameters...
                    ),
                    extractor=JqExtractor(transform=".result[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            configurable_stream(
                name="stats_automations",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/stats_automations.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/automations"),
                        request_parameters_provider=request_parameters_provider(),  # No request parameters...
                    ),
                    extractor=JqExtractor(transform=".results[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="segments",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/segments.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/segments",
                        request_parameters_provider=request_parameters_provider(),  # No request parameters...
                    ),
                    extractor=JqExtractor(transform=".results[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            configurable_stream(
                name="single_sends",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/single_sends.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/singlesends"),
                        # FIXME: would be nice to share the path across streams...
                        request_parameters_provider=request_parameters_provider(),  # No request parameters...
                    ),
                    extractor=JqExtractor(transform=".results[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="templates",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/templates.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="templates"),
                        request_parameters_provider=request_parameters_provider(
                            request_parameters={"generations": "legacy,dynamic"},
                        ),
                    ),
                    extractor=JqExtractor(transform=".templates[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="global_suppressions",
                primary_key="email",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/global_suppressions.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path="suppression/unsubscribes",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                name="suppression_groups",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/suppression_groups.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/groups",
                        request_parameters_provider=request_parameters_provider(),
                    ),
                    extractor=JqExtractor(transform=".[]"),  # Could also the custom extractor above
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            configurable_stream(
                name="suppression_group_members",
                primary_key="group_id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/suppression_group_members.json"),
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/suppressions",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                name="blocks",
                primary_key="email",
                cursor_field=["created"],  # This stream has a cursor field
                schema=JsonSchema("./source_sendgrid/schemas/blocks.json"),
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/blocks",
                        request_parameters_provider=request_parameters_provider(
                            request_parameters={**offset_request_parameters, **cursor_request_parameters},
                        ),
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="bounces",
                primary_key="email",
                cursor_field=["created"],  # This stream has a cursor field
                schema=JsonSchema("./source_sendgrid/schemas/bounces.json"),
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/bounces",
                        request_parameters_provider=request_parameters_provider(
                            request_parameters=cursor_request_parameters,
                        ),
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=NoPagination(),
                ),
            ),
            configurable_stream(
                name="invalid_emails",
                primary_key="email",
                cursor_field=["created"],  # This stream has a cursor field
                schema=JsonSchema("./source_sendgrid/schemas/invalid_emails.json"),
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/invalid_emails",
                        request_parameters_provider=request_parameters_provider(
                            # extract value from stream_state similar to how we're usually doing
                            request_parameters={**offset_request_parameters, **cursor_request_parameters},
                        ),
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                name="spam_reports",
                primary_key="email",
                cursor_field=["created"],  # This stream has a cursor field
                schema=JsonSchema("./source_sendgrid/schemas/spam_reports.json"),
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/spam_reports",
                        request_parameters_provider=request_parameters_provider(
                            # extract value from stream_state similar to how we're usually doing
                            request_parameters={**offset_request_parameters, **cursor_request_parameters},
                        ),
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
        ]

        return streams

    # Define how to check the connection
    def connection_checker(self):
        return CheckStream(self)
