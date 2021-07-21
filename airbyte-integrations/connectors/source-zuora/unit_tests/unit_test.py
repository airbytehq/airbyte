#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
from typing import Any, Dict, Mapping
from source_zuora.zuora_auth import ZuoraAuthenticator
from source_zuora.zuora_client import ZoqlExportClient


class TestClient:

    # read config from test_input/secrets/config.json
    def _config() -> Mapping[str, Any]:
            with open("secrets/config.json", "r") as f:
                return json.loads(f.read())

    # Make instance of ZoqlExportClient using credentials
    def client(config: Dict = _config()):
        # Reading config from the input
        auth_client = ZuoraAuthenticator(config["is_sandbox"])
        authenticator = auth_client.generateToken(config["client_id"], config["client_secret"]).get("header")
        zuora_client = ZoqlExportClient(authenticator=authenticator, url_base=auth_client.endpoint, **config)
        return zuora_client


# Output example from ZoqlExportClient.zuora_get_json_schema 
zuora_schema = [
    {'field': 'field_1', 'type': 'date'},
    {'field': 'field_2', 'type': 'varchar'}, 
    {'field': 'field_3', 'type': 'decimal(22,9)'},
    {'field': 'field_4', 'type': 'timestamp with time zone'},
    {'field': 'field_5', 'type': 'integer'}, 
    {'field': 'field_6', 'type': 'bigint'},
    {'field': 'field_7', 'type': 'zoql'},
]

# Output expected from ZoqlExportClient.convert_schema_types
json_schema = {
    'field_1': {'type': ['string', 'null']}, 
    'field_2': {'type': ['string', 'null']}, 
    'field_3': {'type': ['number', 'null']}, 
    'field_4': {'type': ['string', 'null']}, 
    'field_5': {'type': ['number', 'null']}, 
    'field_6': {'type': ['number', 'null']},
    'field_7': {'type': ['object', 'null']}
}


# TEST 3 - CAST ZUORA SCHEMA TO JSON SCHEMA
def test_cast_schema():
    casted_schema = TestClient.client().convert_schema_types(schema=zuora_schema)
    assert casted_schema == json_schema
