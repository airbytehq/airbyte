#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources.cac.checks.check_stream import CheckStream
from airbyte_cdk.sources.cac.configurable_connector import ConfigurableConnector
from airbyte_cdk.sources.cac.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.cac.extractors.extractor import Extractor
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator
from airbyte_cdk.sources.cac.iterators.only_once import OnlyOnceIterator
from airbyte_cdk.sources.cac.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.cac.requesters.paginators.interpolated_paginator import InterpolatedPaginator
from airbyte_cdk.sources.cac.requesters.paginators.next_page_url_paginator import NextPageUrlPaginator
from airbyte_cdk.sources.cac.requesters.paginators.no_pagination import NoPagination
from airbyte_cdk.sources.cac.requesters.paginators.offset_pagination import OffsetPagination
from airbyte_cdk.sources.cac.requesters.request_params.interpolated_request_parameter_provider import InterpolatedRequestParameterProvider
from airbyte_cdk.sources.cac.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.cac.schema.json_schema import JsonSchema
from airbyte_cdk.sources.cac.states.dict_state import DictState
from airbyte_cdk.sources.cac.states.no_state import NoState
from airbyte_cdk.sources.cac.types import Record
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class SendGridExtractor(Extractor):
    def __init__(self, data_field: Optional[str]):
        self.data_field = data_field

    def extract_records(self, response: requests.Response) -> List[Record]:
        decoded = response.json()
        print(f"decoded: {decoded}")
        if self.data_field:
            return decoded.get(self.data_field, [])
        else:
            return decoded


class SendgridSource(ConfigurableConnector):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return CheckStream(self.streams(config)[0]).check_connection(logger, config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["apikey"])
        limit = 50
        streams = [
            ConfigurableStream(
                name="segments",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/segments.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        url_base="https://api.sendgrid.com/v3/",
                        path="marketing/segments",
                        method="GET",
                        authenticator=authenticator,
                        request_parameters_provider=InterpolatedRequestParameterProvider(request_parameters={}, config=config),
                    ),
                    extractor=SendGridExtractor("results"),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=NoPagination(),
                ),
            ),
            ConfigurableStream(
                name="bounces",
                primary_key="email",
                cursor_field=["created"],
                schema=JsonSchema("./source_sendgrid/schemas/bounces.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        url_base="https://api.sendgrid.com/v3/",
                        path="suppression/bounces",
                        method="GET",
                        authenticator=authenticator,
                        request_parameters_provider=InterpolatedRequestParameterProvider(
                            request_parameters={"start_time": "{{ stream_state['created'] }}", "end_time": "{{ utc_now() }}"},
                            config=config,
                        ),
                    ),
                    extractor=SendGridExtractor(None),
                    iterator=DatetimeIterator(
                        {"value": "{{ stream_state['created'] }}", "default": "{{ config['start_time'] }}"},
                        {"value": "{{ today_utc() }}"},
                        "1000d",
                        "{{ stream_state['created'] }}",
                        "%Y-%m-%d",
                        None,
                        config,
                    ),
                    state=DictState("created", "{{ last_record['created'] }}", state_type=int),
                    paginator=NextPageUrlPaginator(
                        "https://api.sendgrid.com/v3/",
                        InterpolatedPaginator({"next_page_url": "{{ decoded_response['_metadata']['next'] }}"}, config),
                    ),
                ),
            ),
            ConfigurableStream(
                name="suppression_group_members",
                primary_key="group_id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/suppression_group_members.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        url_base="https://api.sendgrid.com/v3/",
                        path="asm/suppressions",
                        method="GET",
                        authenticator=authenticator,
                        request_parameters_provider=InterpolatedRequestParameterProvider(
                            request_parameters={"offset": "{{ next_page_token['offset'] }}", "limit": limit},
                            config=config,
                        ),
                    ),
                    extractor=SendGridExtractor(None),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
                    paginator=OffsetPagination(limit, "offset"),
                ),
            ),
        ]

        return streams
