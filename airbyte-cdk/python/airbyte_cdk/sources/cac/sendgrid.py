#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.cac import create_partial
from airbyte_cdk.sources.cac.checks.check_stream import CheckStream
from airbyte_cdk.sources.cac.configurable_source import ConfigurableSource
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


class SendgridSource(ConfigurableSource):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Define some shared constants
        limit = 50

        # Pagination
        metadata_paginator = NextPageUrlPaginator(
            interpolated_paginator=InterpolatedPaginator({"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}, config),
        )

        # Request parameters
        offset_request_parameters = {"offset": "{{ next_page_token['offset'] }}", "limit": limit}

        offset_pagination_request_parameters = InterpolatedRequestParameterProvider(
            request_parameters=offset_request_parameters,
            config=config,
        )
        cursor_request_parameters = {
            "start_time": "{{ stream_state['created'] }}",
            "end_time": "{{ utc_now() }}",
        }
        cursor_request_parameter_provider = create_partial.create(
            InterpolatedRequestParameterProvider, request_parameters=cursor_request_parameters, config=config
        )
        cursor_offset_parameters = {**offset_request_parameters, **cursor_request_parameters}
        cursor_offset_request_parameter_provider = create_partial.create(
            InterpolatedRequestParameterProvider, request_parameters=cursor_offset_parameters, config=config
        )
        request_parameters_provider = create_partial.create(InterpolatedRequestParameterProvider, config=config)

        # Iterators
        datetime_iterator = DatetimeIterator(
            InterpolatedString("{{ stream_state['created'] }}", "{{ config['start_time'] }}"),
            InterpolatedString("{{ today_utc() }}"),
            step="1000d",
            cursor_value=InterpolatedString("{{ stream_state['created'] }}"),
            datetime_format="%Y-%m-%d",
            config=config,
        )

        # State
        cursor_state = DictState("created", "{{ last_record['created'] }}", state_type=int)

        # Next page url
        next_page_url_from_token_partial = create_partial.create(InterpolatedString, string="{{ next_page_token['next_page_url'] }}")

        simple_retriever = create_partial.create(
            SimpleRetriever, state=NoState(), iterator=OnlyOnceIterator(), paginator=NoPagination(), config=config
        )

        configurable_stream = create_partial.create(
            ConfigurableStream,
            schema_loader=create_partial.create(JsonSchema, file_path="./source_sendgrid/schemas/{{kwargs['name']}}.json"),
            cursor_field=[],
        )
        http_requester = create_partial.create(
            HttpRequester,
            url_base="https://api.sendgrid.com/v3/",
            config=config,
            http_method=HttpMethod.GET,
            authenticator=TokenAuthenticator(config["apikey"]),
            request_parameters_provider=request_parameters_provider(),
        )

        # Define the streams
        streams = [
            configurable_stream(
                kwargs={"name": "lists"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/lists"),
                    ),
                    paginator=metadata_paginator,
                    extractor=JqExtractor(".result[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "campaigns"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/campaigns"),
                    ),
                    extractor=JqExtractor(transform=".result[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "contacts"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/contacts",
                    ),
                    extractor=JqExtractor(transform=".result[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "stats_automations"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/automations"),
                        request_parameters_provider=request_parameters_provider(),
                    ),
                    extractor=JqExtractor(transform=".results[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "segments"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/segments",
                    ),
                    extractor=JqExtractor(transform=".results[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "single_sends"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/singlesends"),
                    ),
                    extractor=JqExtractor(transform=".results[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "templates"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="templates"),
                        request_parameters_provider=request_parameters_provider(
                            request_parameters={"generations": "legacy,dynamic"},
                        ),
                    ),
                    extractor=JqExtractor(transform=".templates[]"),  # Could also the custom extractor above
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "global_suppressions"},
                primary_key="email",
                retriever=simple_retriever(
                    requester=http_requester(
                        path="suppression/unsubscribes",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                kwargs={"name": "suppression_groups"},
                primary_key="id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/groups",
                    ),
                    extractor=JqExtractor(transform=".[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "suppression_group_members"},
                primary_key="group_id",
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/suppressions",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                kwargs={"name": "blocks"},
                primary_key="email",
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/blocks",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "bounces"},
                primary_key="email",
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/bounces",
                        request_parameters_provider=cursor_request_parameter_provider,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "invalid_emails"},
                primary_key="email",
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/invalid_emails",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "spam_reports"},
                primary_key="email",
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=datetime_iterator,
                    requester=http_requester(
                        path="suppression/spam_reports",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
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
