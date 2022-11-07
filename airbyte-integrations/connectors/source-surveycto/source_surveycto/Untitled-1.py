#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from bigquery_schema_generator.generate_schema import SchemaGenerator
from gbqschema_converter.gbqschema_to_jsonschema import json_representation as converter
import json
import sys


from abc import ABC
from imaplib import _Authenticator
from pydoc import doc
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from datetime import datetime, timedelta 
from  dateutil.parser import parse

import requests
import asyncio
import base64
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, NoAuth


class SurveyStream(HttpStream, ABC):

    def __init__(self, config: Mapping[str, Any], form_id, **kwargs):
        super().__init__()

        self.config = config
        self.server_name = config['server_name']
        self.form_id = form_id
        self.start_date = config['start_date']
        #base64 encode username and password as auth token
        user_name_password = f"{config['username']}:{config['password']}"
        self.auth_token = self._base64_encode(user_name_password)

    @property
    def url_base(self) -> str:
         return f"https://{self.server_name}.surveycto.com/api/v2/forms/data/wide/json/"

    def _base64_encode(self,string:str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        
        return {}

class CollectionSchema(SurveyStream):

    primary_key = None

    @property
    def name(self) -> str:
        return self.form_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def _base64_encode(self,string:str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
         return {'date': self.start_date}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Authorization': 'Basic ' + self.auth_token }

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
         return self.form_id

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        self.response_json = response.json()
       
        return self.response_json


class SurveyctoStream(SurveyStream):

    primary_key = None

    @property
    def name(self) -> str:
        return self.form_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def _base64_encode(self,string:str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    def list_data_one(self):
        schema = CollectionSchema(config = self.config, form_id = self.form_id)
        schema_records = schema.read_records(sync_mode="full_refresh")
        print(f'------------>>>>>>{schema_records}')
        list_data = []
        for i in schema_records:
            list_data.append(i)
        return list_data
        

    def get_json_schema(self):
        data = self.list_data_one()
        generator = SchemaGenerator(input_format='dict', infer_mode='NULLABLE',preserve_input_sort_order='true')

        schema_map, error_logs = generator.deduce_schema(input_data=data)
        schema = generator.flatten_schema(schema_map)
        schema_json = converter(schema)
        schema_json_properties=schema_json['definitions']['element']['properties']
        b = json.dumps(schema_json_properties)
        print(f'==============================================>>>>{b}')
  
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": b
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
         return {'date': self.start_date}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'Authorization': 'Basic ' + self.auth_token }

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
         return self.form_id

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        self.response_json = response.json()
    
        for data in self.response_json:
            try:
                yield data
            except Exception as e:
                msg = f"""Encountered an exception parsing schema"""
                self.logger.exception(msg)
                raise e

# Source
class SourceSurveycto(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def no_auth(self):
        return NoAuth()     

    def generate_streams(self, config: str) -> List[Stream]:
        forms = config.get("form_id", [])
        for form_id in forms:
            yield SurveyctoStream(
                config=config,
                form_id=form_id
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # auth = TokenAuthenticator(token="api_key")  # Oauth2Authenticator is also available if you need oauth support
        # return [Customers(authenticator=auth), Employees(authenticator=auth)]
        # auth = NoAuth()        

        streams = self.generate_streams(config=config)
        return streams


