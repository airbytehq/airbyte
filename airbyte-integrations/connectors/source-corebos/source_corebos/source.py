"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
#from typing import Dict, Generator
import requests

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from base_python import AirbyteLogger, Source


class SourceCorebos(Source):
    def _call_api(link):
        return requests.get(link)
    def check(config):
        response = SourceCorebos._call_api(link="http://localhost/corebos/webservice.php?username=admin&operation=getchallenge")
        if response.status_code == 200:
            result = {"status": "SUCCEEDED"}
        else:
            result = {"status": "FAILED", "message": "Input configuration is incorrect."}
            output_message = {"type": "CONNECTION_STATUS", "connectionStatus": result}
            print(json.dumps(output_message))

    def discover():
        catalog = {
            "streams": [
                {
                    "name": "retrieve",
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "result": {
                                "type": "object",
                                "properties": {
                                    "user_name": {"type": "string"},
                                    "is_admin": {"type": "string"},
                                    "email1": {"type": "string"},
                                    "status": {"type": "string"},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "roleid": {"type": "string"},
                                    "currency_id": {"type": "string"},
                                    "currency_grouping_pattern": {"type": "string"},
                                    "currency_decimal_separator": {"type": "string"},
                                    "currency_grouping_separator": {"type": "string"},
                                    "currency_symbol_placement": {"type": "string"},
                                    "no_of_currency_decimals": {"type": "string"},
                                    "lead_view": {"type": "string"},
                                    "activity_view": {"type": "string"},
                                    "hour_format": {"type": "string"},
                                    "signature": {"type": "string"},
                                    "start_hour": {"type": "string"},
                                    "end_hour": {"type": "string"},
                                    "title": {"type": "string"},
                                    "phone_fax": {"type": "string"},
                                    "department": {"type": "string"},
                                    "email2": {"type": "string"},
                                    "phone_work": {"type": "string"},
                                    "secondaryemail": {"type": "string"},
                                    "phone_mobile": {"type": "string"},
                                    "reports_to_id": {"type": "string"},
                                    "phone_home": {"type": "string"},
                                    "phone_other": {"type": "string"},
                                    "date_format": {"type": "string"},
                                    "description": {"type": "string"},
                                    "time_zone": {"type": "string"},
                                    "internal_mailer": {"type": "string"},
                                    "theme": {"type": "string"},
                                    "language": {"type": "string"},
                                    "send_email_to_sender": {"type": "string"},
                                    "address_street": {"type": "string"},
                                    "address_country": {"type": "string"},
                                    "address_city": {"type": "string"},
                                    "address_postalcode": {"type": "string"},
                                    "address_state": {"type": "string"},
                                    "id": {"type": "string"},
                                    "rolename": {"type": "string"},
                                    "currency_idename": {
                                        "type": "object",
                                        "properties": {
                                            "module": {"type": "string"},
                                            "reference": {"type": "string"},
                                            "cbuuid": {"type": "string"},
                                        },
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        airbyte_message = {"type": "CATALOG", "catalog": catalog}
        print(json.dumps(airbyte_message))

    def read(config, catalog):
        retrieve_stream = None
        for configured_stream in catalog["streams"]:
            if configured_stream["stream"]["name"] == "retrieve":
                retrieve_stream = configured_stream

        if retrieve_stream is None:
            SourceCorebos.log("No streams selected")
            return
        link = "http://localhost/corebos/webservice.php?operation=retrieve&sessionName="+config["sessionName"]+"&id=19x1"
        response = SourceCorebos._call_api(link)
        if response.status_code != 200:
            SourceCorebos.log("Failure occurred when calling coreBOS API")
            sys.exit(1)
        else:
            collections = response.json()
            for collection in collections:
                data = {"success": collection["success"], "result": collection["result"]}
                record = {"stream": "retrieve", "data": data}
                output_message = {"type": "RECORD", "record": record}
                print(json.dumps(output_message))

    def log(message):
        log_json = {"type": "LOG", "log": message}
        print(json.dumps(log_json))
