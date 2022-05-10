#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.cac.configurable_stream import ConfigurableStream
from airbyte_cdk.sources.cac.extractors.extractor import Extractor
from airbyte_cdk.sources.cac.iterators.datetime_iterator import DatetimeIterator
from airbyte_cdk.sources.cac.iterators.only_once import OnlyOnceIterator
from airbyte_cdk.sources.cac.requesters.http_requester import HttpRequester
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
        if self.data_field:
            return decoded.get(self.data_field, [])
        else:
            return decoded


class SendgridSource(AbstractSource):
    def _load_config(self):
        # TODO is it better to do package loading?
        print(f"path: {self._path_to_spec}")
        print(f"path: {os.path}")
        print(f"os.listdir: {os.listdir()}")
        with open(self._path_to_spec, "r") as f:
            return json.loads(f.read())

    def get_spec_obj(self):
        try:
            with open("/airbyte/integration_code/source_sendgrid/spec.json", "r") as f:
                return json.loads(f.read())
        except RuntimeError:
            with open("./source_sendgrid/spec.json", "r") as f:
                return json.loads(f.read())

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            gen = self.streams(config)[0].read_records(sync_mode=SyncMode.full_refresh)
            next(gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Sendgrid API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
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
                        authenticator=TokenAuthenticator(config["apikey"]),
                    ),
                    extractor=SendGridExtractor("results"),
                    iterator=OnlyOnceIterator(),
                    state=NoState(),
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
                        authenticator=TokenAuthenticator(config["apikey"]),
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
                    state=DictState("created", "{{ last_record['created'] }}"),
                ),
            ),
        ]

        return streams


def load_json(path):
    with open(path, "r") as f:
        return json.loads(f.read())
