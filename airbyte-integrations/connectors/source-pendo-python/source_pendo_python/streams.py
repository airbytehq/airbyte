from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class PendoPythonStream(HttpStream, ABC):
    url_base = "https://app.pendo.io/api/v1/"
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {}

    def get_valid_type(self, field_type) -> str:
        if field_type == 'time':
            return 'integer'
        if field_type == 'list':
            return 'array'
        return field_type


class Feature(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "feature"


class Guide(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "guide"


class Page(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "page"


class Report(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "report"


class VisitorMetadata(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "metadata/schema/visitor"


class AccountMetadata(PendoPythonStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "metadata/schema/account"


class Visitors(PendoPythonStream):
    primary_key = "visitorId"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "aggregation"

    @property
    def http_method(self) -> str:
        return "POST"

    def get_json_schema(self) -> Mapping[str, Any]:
        print("Got called")
        base_schema = super().get_json_schema()
        url = f"{PendoPythonStream.url_base}metadata/schema/visitor"
        auth_headers = self.authenticator.get_auth_header()
        try:
            session = requests.get(url, headers=auth_headers)
            body = session.json()

            full_schema = base_schema

            auto_fields = {}
            for key in body['auto']:
                auto_fields[key] = {
                    "type": ["null", self.get_valid_type(body['auto'][key]['Type'])]
                }
            full_schema['properties']['metadata']['properties']['auto']['properties'] = auto_fields

            agent_fields = {}
            for key in body['agent']:
                agent_fields[key] = {
                    "type": ["null", self.get_valid_type(body['agent'][key]['Type'])]
                }
            full_schema['properties']['metadata']['properties']['agent']['properties'] = agent_fields
            return full_schema
        except requests.exceptions.RequestException:
            return base_schema

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        return {
            "response": {
                "mimeType": "application/json"
            },
            "request": {
                "requestId": "visitor-list",
                "pipeline": [
                    {
                        "source": {
                            "visitors": {
                                "identified": True
                            }
                        }
                    },
                    {
                        "sort": ["visitorId"]
                    }
                ]
            }
        }

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargss
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get("results", [])


class Accounts(PendoPythonStream):
    primary_key = "accountId"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "aggregation"

    @property
    def http_method(self) -> str:
        return "POST"

    def get_valid_type(self, field_type) -> str:
        if field_type == 'time':
            return 'integer'
        if field_type == 'list':
            return 'array'
        return field_type

    def get_json_schema(self) -> Mapping[str, Any]:
        print("Got called")
        base_schema = super().get_json_schema()
        url = f"{PendoPythonStream.url_base}metadata/schema/account"
        auth_headers = self.authenticator.get_auth_header()
        try:
            session = requests.get(url, headers=auth_headers)
            body = session.json()

            full_schema = base_schema

            auto_fields = {}
            for key in body['auto']:
                auto_fields[key] = {
                    "type": ["null", self.get_valid_type(body['auto'][key]['Type'])]
                }
            full_schema['properties']['metadata']['properties']['auto']['properties'] = auto_fields

            agent_fields = {}
            for key in body['agent']:
                agent_fields[key] = {
                    "type": ["null", self.get_valid_type(body['agent'][key]['Type'])]
                }
            full_schema['properties']['metadata']['properties']['agent']['properties'] = agent_fields
            return full_schema
        except requests.exceptions.RequestException:
            return base_schema

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ):
        return {
            "response": {
                "mimeType": "application/json"
            },
            "request": {
                "requestId": "account-list",
                "pipeline": [
                    {
                        "source": {
                            "accounts": {}
                        }
                    },
                    {
                        "sort": ["accountId"]
                    }
                ]
            }
        }

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargss
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get("results", [])
