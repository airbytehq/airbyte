#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.lcc import create_partial
from airbyte_cdk.sources.lcc.checks.check_stream import CheckStream
from airbyte_cdk.sources.lcc.configurable_source import ConfigurableSource
from airbyte_cdk.sources.lcc.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.lcc.extractors.jq import JqExtractor
from airbyte_cdk.sources.lcc.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.lcc.requesters.http_requester import HttpMethod, HttpRequester
from airbyte_cdk.sources.lcc.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.lcc.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.lcc.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.lcc.requesters.paginators.offset_pagination import OffsetPagination
from airbyte_cdk.sources.lcc.requesters.request_params.interpolated_request_parameter_provider import InterpolatedRequestParameterProvider
from airbyte_cdk.sources.lcc.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.lcc.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.lcc.schema.json_schema import JsonSchema
from airbyte_cdk.sources.lcc.states.dict_state import DictState
from airbyte_cdk.sources.lcc.states.no_state import NoState
from airbyte_cdk.sources.lcc.stream_slicers.datetime_stream_slicer import DatetimeStreamSlicer
from airbyte_cdk.sources.lcc.stream_slicers.single_slice import SingleSlice
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

        # Stream Slicer
        stream_slicer = DatetimeStreamSlicer(
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
            SimpleRetriever,
            name="{{ kwargs['name'] }}",
            state=NoState(),
            iterator=SingleSlice(),
            paginator=NoPagination(),
            primary_key="{{ kwargs['primary_key'] }}",
        )

        configurable_stream = create_partial.create(
            ConfigurableStream,
            schema_loader=create_partial.create(JsonSchema, file_path="./source_sendgrid/schemas/{{kwargs['name']}}.json"),
            cursor_field=[],
        )
        http_requester = create_partial.create(
            HttpRequester,
            name="{{ kwargs['name'] }}",
            url_base="https://api.sendgrid.com/v3/",
            config=config,
            http_method=HttpMethod.GET,
            authenticator=TokenAuthenticator(config["apikey"]),
            request_parameters_provider=request_parameters_provider(),
            retrier=DefaultRetrier(),
        )

        jq = create_partial.create(JqExtractor, config=config)

        # Define the streams
        streams = [
            configurable_stream(
                kwargs={"name": "lists", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/lists"),
                    ),
                    paginator=metadata_paginator,
                    extractor=jq(".result[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "campaigns", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/campaigns"),
                    ),
                    extractor=jq(transform=".result[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "contacts", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/contacts",
                    ),
                    extractor=jq(transform=".result[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "stats_automations", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/automations"),
                        request_parameters_provider=request_parameters_provider(),
                    ),
                    extractor=jq(transform=".results[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "segments", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path="marketing/segments",
                    ),
                    extractor=jq(transform=".results[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "single_sends", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="marketing/stats/singlesends"),
                    ),
                    extractor=jq(transform=".results[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "templates", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path=next_page_url_from_token_partial(default="templates"),
                        request_parameters_provider=request_parameters_provider(
                            request_parameters={"generations": "legacy,dynamic"},
                        ),
                    ),
                    extractor=jq(transform=".templates[]"),  # Could also the custom extractor above
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "global_suppressions", "primary_key": "email"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path="suppression/unsubscribes",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=jq(transform=".[]"),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                kwargs={"name": "suppression_groups", "primary_key": "id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/groups",
                    ),
                    extractor=jq(transform=".[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "suppression_group_members", "primary_key": "group_id"},
                retriever=simple_retriever(
                    requester=http_requester(
                        path="asm/suppressions",
                        request_parameters_provider=offset_pagination_request_parameters,
                    ),
                    extractor=jq(transform=".[]"),
                    paginator=OffsetPagination(limit),
                ),
            ),
            configurable_stream(
                kwargs={"name": "blocks", "primary_key": "email"},
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=stream_slicer,
                    requester=http_requester(
                        path="suppression/blocks",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
                    ),
                    extractor=jq(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "bounces", "primary_key": "email"},
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=stream_slicer,
                    requester=http_requester(
                        path="suppression/bounces",
                        request_parameters_provider=cursor_request_parameter_provider,
                    ),
                    extractor=jq(transform=".[]"),
                ),
            ),
            configurable_stream(
                kwargs={"name": "invalid_emails", "primary_key": "email"},
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=stream_slicer,
                    requester=http_requester(
                        path="suppression/invalid_emails",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
                    ),
                    extractor=jq(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
            configurable_stream(
                kwargs={"name": "spam_reports", "primary_key": "email"},
                cursor_field=["created"],
                retriever=simple_retriever(
                    state=cursor_state,
                    iterator=stream_slicer,
                    requester=http_requester(
                        path="suppression/spam_reports",
                        request_parameters_provider=cursor_offset_request_parameter_provider,
                    ),
                    extractor=jq(transform=".[]"),
                    paginator=metadata_paginator,
                ),
            ),
        ]

        return streams

    # Define how to check the connection
    def connection_checker(self):
        return CheckStream(self)
