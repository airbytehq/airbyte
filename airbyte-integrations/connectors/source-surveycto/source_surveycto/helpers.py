
from typing import Any, Dict

import requests
import base64
from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from bigquery_schema_generator.generate_schema import SchemaGenerator
from gbqschema_converter.gbqschema_to_jsonschema import json_representation as converter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry



class Helpers(object):

    @staticmethod
    def _base64_encode(string:str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    @staticmethod
    def call_survey_cto(config, form_id):
        server_name = config['server_name']
        start_date = config['start_date']
        user_name_password = f"{config['username']}:{config['password']}"
        auth_token = Helpers._base64_encode(user_name_password)
        
        url = f"https://{server_name}.surveycto.com/api/v2/forms/data/wide/json/{form_id}?date={start_date}"

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 409],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        response = http.get(url, headers = {'Authorization': 'Basic ' + auth_token })
        data = response.json()
        generator = SchemaGenerator(input_format='dict', infer_mode='NULLABLE',preserve_input_sort_order='true')

        schema_map, error_logs = generator.deduce_schema(input_data=data)
        schema = generator.flatten_schema(schema_map)
        schema_json = converter(schema)
        schema=schema_json['definitions']['element']['properties']    
        return schema

    @staticmethod
    def get_json_schema(schema):

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": schema,
        }
        return json_schema

    @staticmethod
    def get_airbyte_stream(form_id: str, json_schema: Dict[str, Any]) -> AirbyteStream:
        return AirbyteStream(
            name=form_id,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        )
