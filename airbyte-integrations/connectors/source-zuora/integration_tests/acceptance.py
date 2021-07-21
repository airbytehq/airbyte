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
import pytest
from typing import Any, Dict, Mapping
from source_zuora.zuora_auth import ZuoraAuthenticator
from source_zuora.zuora_client import ZoqlExportClient


# read config from test_input/secrets/config.json
def _config() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())

class TestClient:
    # Make instance of ZoqlExportClient using credentials
    def client(config: Dict = _config()):
        # Reading config from the input
        auth_client = ZuoraAuthenticator(config["is_sandbox"])
        authenticator = auth_client.generateToken(config["client_id"], config["client_secret"]).get("header")
        zuora_client = ZoqlExportClient(authenticator=authenticator, url_base=auth_client.endpoint, **config)
        return zuora_client


# TEST 1 - CAST ZUORA SCHEMA TO JSON SCHEMA
def test_zuora_list_streams():
    zuora_streams_list = TestClient.client().zuora_list_streams()
    assert True if zuora_streams_list is not None else False

# TEST 2 - CAST ZUORA SCHEMA TO JSON SCHEMA
def test_zuora_get_json_schema():
    test_obj = "account"
    json_schema = TestClient.client().zuora_get_json_schema(test_obj)
    # print(json_schema)
    assert True if "id" in json_schema.keys() else False