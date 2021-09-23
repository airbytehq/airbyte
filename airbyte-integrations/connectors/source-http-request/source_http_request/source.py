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


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import json
import csv
import pandas as pd
import numbers

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode, AirbyteMessage, AirbyteRecordMessage, Type
from datetime import datetime, timedelta
from io import StringIO
from dateutil.parser import parse


class HttpRequest(HttpStream):
    url_base = ""
    cursor_field = ""
    primary_key = ""

    def __init__(self, url: str, http_method: str, headers: Optional[str], body: Optional[str], response_format: Optional[str], response_delimiter: Optional[str], json_source: Optional[str], json_field: Optional[str]):
        super().__init__()
        self.url_base = url
        self._http_method = http_method
        self._headers = headers
        self._body = body
        self._response_format = response_format
        self._response_delimiter = response_delimiter
        self._json_source = json_source
        self._json_field = json_field

    @property
    def http_method(self) -> str:
        return self._http_method

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        if self._headers:
            return self._headers

        return {}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        if self._body:
            return self._body
        return None

    def _make_request(self):
        http_method = self._http_method.lower()
        url = self.url_base
        headers = self._headers
        body = self._body

        if http_method == "get":
            r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r

    def get_json_schema(self):
        schema = super().get_json_schema()

        resp = self._make_request()
        if resp.status_code == 200:
            if self._response_format == "csv":
                data = resp.content
                df = pd.read_csv(StringIO(data.decode('utf-8')), nrows=3, sep=self._response_delimiter)
                headers = df.columns.tolist()
            elif self._response_format == "json":
                root = json.loads(resp.content)
                if self._json_source == "root":
                    df = pd.DataFrame.from_dict(root)
                else:
                    df = pd.DataFrame.from_dict(root[self._json_field])
                headers = df.columns.tolist()

        properties = {}
        for header in headers:
            _type = "string"
            try:
                if isinstance(df.loc[0, header], numbers.Number):
                    _type = "number"
                elif isinstance(df.loc[0, header], dict):
                    _type = "object"

                parse(df.loc[0, header])
                _type = "date"
            except:
                pass

            properties[header] = {"description": "", "type": _type}

        new_schema = schema
        new_schema["required"] = []
        new_schema["properties"] = properties

        return new_schema

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if self._response_format == "csv":
            decoded = response.content.decode('utf-8')
            data = csv.DictReader(decoded.splitlines(), delimiter=self._response_delimiter)
            yield from data
        elif self._response_format == "json":
            print("BEFORE")
            root = json.loads(response.content)
            if self._json_source == "root":
                yield from root
            else:
                yield from root[self._json_field]
        else:
            raise Exception("Invalid response format")

class SourceHttpRequest(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            resp = self._make_request(config, logger)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None

            error = resp.json().get("error")
            code = error.get("code")
            message = error.get("message") or error.get("info")

            return False, message
        except Exception as e:
            return False, e

    def _make_request(self, config, logger):
        parsed_config = self._parse_config(config)
        http_method = parsed_config.get("http_method").lower()
        url = parsed_config.get("url")
        headers = parsed_config.get("headers", {})
        body = parsed_config.get("body", {})

        if http_method == "get":
            r = requests.get(url, headers=headers, json=body)
        elif http_method == "post":
            r = requests.post(url, headers=headers, json=body)
        else:
            raise Exception(f"Did not recognize http_method: {http_method}")

        return r

    def _is_valid_date(self, value):
        if value == "current":
            return True
        elif len(value.split(" ")) == 3:
            _value = value.replace("current ", "")
            if "-" in _value and _value.replace("- ", "").isdigit():
                return True
            elif "+" in _value and _value.replace("+ ", "").isdigit():
                return True
        return False

    def _get_value(self, value, unit):
        if self._is_valid_date(value):
            if value == "current":
                return datetime.today()
            elif "-" in value:
                digit = int(value.replace("current - ", ""))
                if unit == "day":
                    return datetime.today() - timedelta(days = digit)
                if unit == "month":
                    return datetime.today() - timedelta(month = digit)
                if unit == "year":
                    return datetime.today() - timedelta(year = digit)
            elif "+" in value:
                digit = int(value.replace("current + ", ""))
                if unit == "day":
                    return datetime.today() + timedelta(days = digit)
                if unit == "month":
                    return datetime.today() + timedelta(month = digit)
                if unit == "year":
                    return datetime.today() + timedelta(year = digit)

        raise Exception("Params malformed")

    def _parse_config(self, config):
        url = config.get("url")
        params = json.loads(config.get("params", "[]"))

        try:
            for param in params:
                if param["type"] == "date":
                    if param["variable"] in url:
                        value = self._get_value(param["value"], param["unit"]).strftime(param["format"])

                        url = url.replace("{{{}}}".format(param["variable"]), value)
                    else:
                        raise Exception("Params not informed in the URL")
                elif param["type"] == "period":
                    if param["start_date"]:
                        if param["start_date"]["variable"] in url:
                            value = self._get_value(param["start_date"]["value"], param["unit"]).strftime(param["format"])

                            url = url.replace("{{{}}}".format(param["start_date"]["variable"]), value)

                            if param["end_date"]:
                                if param["end_date"]["variable"] in url:
                                    value = self._get_value(param["end_date"]["value"], param["unit"]).strftime(param["format"])

                                    url = url.replace("{{{}}}".format(param["end_date"]["variable"]), value)
                                else:
                                    raise Exception("Params not informed in the URL")
                            else:
                                raise Exception("Params end_date not informed")
                        else:
                            raise Exception("Params not informed in the URL")
                    else:
                        raise Exception("Params start_date not informed")
                else:
                    raise Exception("Params invalid")

        except Exception as e:
            raise e

        return {
            "url": url,
            "http_method": config.get("http_method", "GET"),
            "headers": json.loads(config.get("headers", "{}")),
            "body": json.loads(config.get("body", "{}")),
            "response_format": config.get("response_format", "json"),
            "response_delimiter": config.get("response_delimiter", ","),
            "json_source": config.get("json_source", "root"),
            "json_field": config.get("json_field", ""),
        }


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        parsed_config = self._parse_config(config)
        return [HttpRequest(parsed_config["url"], parsed_config["http_method"], parsed_config.get("headers"), parsed_config.get("body"), parsed_config.get("response_format"),
                            parsed_config.get("response_delimiter"), parsed_config.get("json_source"), parsed_config.get("json_field"),)]
