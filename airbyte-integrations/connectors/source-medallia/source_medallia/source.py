#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Dict, Generator, Optional, Mapping, Any, Iterable, List, MutableMapping
import requests

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
)
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources import AbstractSource
from sgqlc.operation import Operation

from .utils import initialize_authenticator
from abc import ABC
from .authenticator import Medalliaauth2Authenticator
from . import medallia_schema
import sgqlc.operation
from .utils import read_full_refresh

_schema = medallia_schema
_schema_root = _schema.medallia_schema


class MedalliaStream(HttpStream, ABC):
    limit = 100
    primary_key = "id"
    http_method = "POST"

    def __init__(self, url_base: str, fields: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_endpoint = url_base
        self.fields = fields

        """Request Field data to use in subsequent queries"""
        if fields:

            self.metadata_columns = fields['metadata_columns']
            self.question_columns = fields['question_columns']

    @property
    def url_base(self) -> str:
        return self.api_endpoint

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 401:
            try:
                self.header = self.auth.get_auth_header()
            except:
                return False
        return response.status_code in [401, 408] or super().should_retry(response)

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()

        yield response_json

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        page_info = response.json()["data"][self.entity]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        if has_next_page:
            self.last_page_cursor = page_info["endCursor"]
            return page_info["endCursor"]
        else:
            return None


class Fields(MedalliaStream):
    entity = 'fields'

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            for r in record['data'][self.entity]['nodes']:
                yield r

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        op = sgqlc.operation.Operation(_schema_root.query_type)
        fields = op.fields(first=self.limit, after=next_page_token)
        fields.nodes.id()
        fields.nodes.name()
        fields.nodes.description()
        fields.nodes.data_type()
        fields.nodes.multivalued()
        fields.nodes.filterable()

        fields.nodes.__as__(_schema.Field).__as__(_schema.EnumField).options()

        fields.page_info()
        fields.page_info.has_next_page()
        fields.page_info.end_cursor()

        return {'query': str(op)}


class FieldId(MedalliaStream):
    entity = 'fields'

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            for r in record['data'][self.entity]['nodes']:
                yield r

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        op = sgqlc.operation.Operation(_schema_root.query_type)
        fields = op.fields(first=10000, after=None)
        fields.nodes.id()
        fields.nodes.name()
        fields.page_info()
        fields.page_info.has_next_page()
        fields.page_info.end_cursor()

        return {'query': str(op)}





class Feedback(MedalliaStream, IncrementalMixin):
    limit = 250
    entity = 'feedback'
    state_checkpoint_interval = 5000
    primary_key = "id"

    cursor_field = 'a_initial_finish_timestamp'
    _cursor_value = 0

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:

        for record in super().read_records(*args, **kwargs):

            for r in record['data'][self.entity]['nodes']:
                for x in r['metaData']:
                    if x['field']['id'] == self.cursor_field:
                        r[self.cursor_field] = x['values'][0]
                        self._cursor_value = max(int(self._cursor_value), int(x['values'][0]))
                yield r

    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        op = sgqlc.operation.Operation(_schema_root.query_type)

        order = {"fieldId": "a_initial_finish_timestamp", "direction": "ASC"}

        filter = {"fieldIds": ["a_initial_finish_timestamp"], "gt": str(self._cursor_value)}

        var = _schema.RecordOrder(order)

        # do not apply after, will have no pages left when all data loaded
        feedback = op.feedback(first=self.limit, order_by=[var], filter=filter)
        feedback.nodes.id()

        extend_field_data = sgqlc.operation.Fragment(_schema_root.FieldData, 'extendFieldData')

        extend_field_data.__as__(_schema_root.EnumFieldData).options()
        extend_field_data.__as__(_schema_root.StringFieldData).values()

        extend_field_data.__as__(_schema_root.CommentFieldData).rule_topic_taggings_page(__alias__='topics').nodes()
        extend_field_data.__as__(_schema_root.CommentFieldData).data_topic_taggings_page(__alias__='themes').nodes()
        extend_field_data.__as__(_schema_root.CommentFieldData).sentiment_taggings_page(__alias__='sentiment').nodes()

        extend_field_data.__as__(_schema_root.IntFieldData).values()
        extend_field_data.__as__(_schema_root.DateFieldData).values()
        extend_field_data.__as__(_schema_root.UnitFieldData).units().id()

        meta_data = feedback.nodes.field_data_list(__alias__='metaData',
                                                   filter_unanswered=True,
                                                   field_ids=self.metadata_columns)

        meta_data.field().id()
        meta_data.field().name()

        meta_data.__fragment__(extend_field_data)

        question_data = feedback.nodes.field_data_list(__alias__='questionData',
                                                       filter_unanswered=True,
                                                       field_ids=self.question_columns)

        question_data.field().id()
        question_data.field().name()

        question_data.__fragment__(extend_field_data)

        feedback.page_info()
        feedback.page_info.has_next_page()
        feedback.page_info.end_cursor()

        return {'query': str(op)}


class SourceMedallia(AbstractSource):

    def get_fields(self, config: json):

        initialization_params = {"authenticator": initialize_authenticator(config), "url_base": config.get("query-endpoint")}

        field_id = FieldId(**initialization_params)

        data = read_full_refresh(field_id)

        nodes = {}

        for node in data:
            nodes[node["id"]] = node

        metadata_columns = list(filter(lambda x: x.startswith(tuple(['a_', 'u_', 'e_', 'k_'])), nodes))
        question_columns = list(filter(lambda x: x.startswith('q_'), nodes))

        fields = {}
        fields['metadata_columns'] = metadata_columns
        fields['question_columns'] = question_columns

        return fields

    def check_connection(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Testing connection availability for the connector by granting the token.
        """

        try:
            fields = self.get_fields(config)
            return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API and is included for completeness.
        # Skip passing an authenticator if no authentication is required.
        # Other authenticators are available for API token-based auth and Oauth2.

        fields = self.get_fields(config)

        initialization_params = {"authenticator": initialize_authenticator(config), "url_base": config.get("query-endpoint"),
                                 "fields": fields}

        return [
            Fields(**initialization_params),
            Feedback(**initialization_params)
        ]
