#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
from datetime import datetime

import requests
from bigquery_schema_generator.generate_schema import SchemaGenerator
from gbqschema_converter.gbqschema_to_jsonschema import json_representation as converter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Helpers(object):
    @staticmethod
    def _base64_encode(string: str) -> str:
        return base64.b64encode(string.encode("ascii")).decode("ascii")

    @staticmethod
    def call_survey_cto(config, form_id):
        server_name = config["server_name"]
        start_date = config["start_date"]
        user_name_password = f"{config['username']}:{config['password']}"
        auth_token = Helpers._base64_encode(user_name_password)

        url = f"https://{server_name}.surveycto.com/" + f"api/v2/forms/data/wide/json/{form_id}?date={start_date}"

        retry_strategy = Retry(total=3, status_forcelist=[429, 409], method_whitelist=["HEAD", "GET", "OPTIONS"])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        response = http.get(url, headers={"Authorization": "Basic " + auth_token})
        response_json = response.json()

        if response.status_code != 200 and response_json["error"]:
            message = response_json["error"]["message"]
            raise Exception(message)

        for data in response_json:
            try:
                dateformat_in = "%b %d, %Y %I:%M:%S %p"
                dateformat_out = "%Y-%m-%dT%H:%M:%S+00:00"
                data["starttime"] = datetime.strptime(data["starttime"], dateformat_in).strftime(dateformat_out)
                data["endtime"] = datetime.strptime(data["endtime"], dateformat_in).strftime(dateformat_out)
                data["CompletionDate"] = datetime.strptime(data["CompletionDate"], dateformat_in).strftime(dateformat_out)
                data["SubmissionDate"] = datetime.strptime(data["SubmissionDate"], dateformat_in).strftime(dateformat_out)
                yield data
            except Exception as e:
                raise e

        return data

    @staticmethod
    def get_filter_data(data):
        generator = SchemaGenerator(input_format="dict", infer_mode="NULLABLE", preserve_input_sort_order="true")

        schema_map, error_logs = generator.deduce_schema(input_data=data)
        schema = generator.flatten_schema(schema_map)
        schema_json = converter(schema)
        schema = schema_json["definitions"]["element"]["properties"]
        return schema

    @staticmethod
    def get_json_schema(schema):
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": schema,
        }
        return json_schema
