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
import time
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, NoAuth
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.sources.streams.core import Stream

from .helpers import Helpers



class SurveyStream(HttpStream, ABC):
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Mapping[str, Any], form_id, schema, **kwargs):
        super().__init__()

        self.config = config
        self.schema = schema
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


class SurveyctoStream(SurveyStream, IncrementalMixin):
    primary_key = 'KEY'
    date_format_scto = '%b %d, %Y %H:%M:%S %p'
    dateformat =  '%Y-%m-%dT%H:%M:%S+00:00'
    cursor_field = 'CompletionDate'
    _cursor_value = None


    @property
    def state(self) -> Mapping[str, Any]:
        initial_date = datetime.strptime(self.start_date, self.date_format_scto)
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: initial_date}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], self.dateformat)
        
    @property
    def name(self) -> str:
        return self.form_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def get_json_schema(self):  
        return self.schema

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        ix = self.state[self.cursor_field] 
        return {'date': ix.strftime(self.date_format_scto)}

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

                key = data["KEY"]
                o = key.replace('uuid:', '')
                data["KEY"] = o
 
                starttime = data["starttime"]
                a = datetime.strptime(starttime, self.date_format_scto).strftime(self.dateformat)
                data["starttime"] = a

                endtime = data["endtime"]
                a = datetime.strptime(endtime, self.date_format_scto).strftime(self.dateformat)
                data["endtime"] = a

                completiondate = data["CompletionDate"]
                a = datetime.strptime(completiondate, self.date_format_scto).strftime(self.dateformat)
                data["CompletionDate"] = a

                submissiondate = data["SubmissionDate"]
                a = datetime.strptime(submissiondate, self.date_format_scto).strftime(self.dateformat)
                data["SubmissionDate"] = a

                
                yield data
            except Exception as e:
                msg = f"""Encountered an exception parsing schema"""
                self.logger.exception(msg)
                raise e
                
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            self._cursor_value = record[self.cursor_field]
            yield record


# Source
class SourceSurveycto(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def no_auth(self):
        return NoAuth()  

    def generate_streams(self, config: str) -> List[Stream]:
        forms = config.get("form_id", [])
        streams = []
      
        for form_id in forms:
            schema = Helpers.call_survey_cto(config, form_id)
            filter_data = Helpers.get_filter_data(schema)
            schema_res = Helpers.get_json_schema(filter_data)
            stream = SurveyctoStream(config=config,form_id=form_id,schema=schema_res)
            streams.append(stream)
        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:    
        streams = self.generate_streams(config=config)
        return streams

