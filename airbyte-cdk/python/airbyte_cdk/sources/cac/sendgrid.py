#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.cac.checks.check_stream import CheckStream
from airbyte_cdk.sources.cac.configurable_connector import ConfigurableConnector
from airbyte_cdk.sources.cac.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.cac.extractors.jq import JqExtractor
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
        print(f"decoded: {decoded}")
        if self.data_field:
            return decoded.get(self.data_field, [])
        else:
            return decoded
"""


class SendgridSource(ConfigurableConnector):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["apikey"])
        limit = 50
        kwargs = {
            "url_base": "https://api.sendgrid.com/v3/",
            "http_method": HttpMethod.GET,
            "authenticator": authenticator,
            "config": config,
        }
        streams = [
            ConfigurableStream(
                name="segments",
                primary_key="id",
                cursor_field=[],
                schema=JsonSchema("./source_sendgrid/schemas/segments.json"),
                retriever=SimpleRetriever(
                    requester=HttpRequester(
                        path="marketing/segments",
                        request_parameters_provider=InterpolatedRequestParameterProvider(kwargs=kwargs),
                        kwargs=kwargs,
                    ),
                    extractor=JqExtractor(transform=".results[]"),
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
                        path="suppression/bounces",
                        request_parameters_provider=InterpolatedRequestParameterProvider(
                            request_parameters={"start_time": "{{ stream_state['created'] }}", "end_time": "{{ utc_now() }}"},
                            config=config,
                        ),
                        kwargs=kwargs,
                    ),
                    extractor=JqExtractor(transform=".[]"),
                    iterator=DatetimeIterator(
                        {"value": "{{ stream_state['created'] }}", "default": "{{ config['start_time'] }}"},
                        {"value": "{{ today_utc() }}"},
                        step="1000d",
                        cursor_value="{{ stream_state['created'] }}",
                        datetime_format="%Y-%m-%d",
                        config=config,
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

    def connection_checker(self):
        return CheckStream(self)
