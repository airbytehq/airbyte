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
        yield from response.json()

    def get_valid_type(self, field_type) -> str:
        if field_type == 'time':
            return 'integer'
        if field_type == 'list':
            return 'array'
        return field_type

    def build_schema(self, full_schema, metadata):
        for key in metadata:
            if not key.startswith("auto"):
                fields = {}
                for field in metadata[key]:
                    field_type = metadata[key][field]['Type']
                    if field_type != '':
                        fields[field] = {
                            "type": ["null", self.get_valid_type(field_type)]
                        }
                    else:
                        fields[field] = {
                            "type": ["null", "array", "string", "integer", "boolean"]
                        }

                full_schema['properties']['metadata']['properties'][key] = {
                    "type": ["null", "object"],
                    "properties": fields
                }
        return full_schema


class PendoAggregationStream(PendoPythonStream):
    json_schema = None
    page_size = 10

    @property
    def http_method(self) -> str:
        return "POST"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "aggregation"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json().get("results", [])
        if len(data) < self.page_size:
            return None
        return data[-1][self.primary_key]

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargss
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        yield from response.json().get("results", [])

    def build_request_body(self, requestId, source, next_page_token) -> Optional[Mapping[str, Any]]:
        request_body = {
            "response": {"mimeType": "application/json"},
            "request": {
                "requestId": requestId,
                "pipeline": [
                    {"source": source},
                    {"sort": [self.primary_key]},
                    {"limit": self.page_size},
                ],
            },
        }

        if next_page_token is not None:
            request_body["request"]["pipeline"].insert(
                2, {"filter": f"{self.primary_key} > \"{next_page_token}\""}
            )

        return request_body


class Feature(PendoPythonStream):
    name = "Feature"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "feature"


class Guide(PendoPythonStream):
    name = "Guide"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "guide"


class Page(PendoPythonStream):
    name = "Page"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "page"


class Report(PendoPythonStream):
    name = "Report"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "report"


class VisitorMetadata(PendoPythonStream):
    name = "Visitor Metadata"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "metadata/schema/visitor"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]


class AccountMetadata(PendoPythonStream):
    name = "Account Metadata"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "metadata/schema/account"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]


class Visitors(PendoAggregationStream):
    primary_key = "visitorId"

    name = "Visitors"

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is None:
            base_schema = super().get_json_schema()
            url = f"{PendoPythonStream.url_base}metadata/schema/visitor"
            auth_headers = self.authenticator.get_auth_header()
            try:
                session = requests.get(url, headers=auth_headers)
                body = session.json()

                full_schema = base_schema
                full_schema['properties']['metadata']['properties']['auto__323232'] = {
                    "type": ["null", "object"]
                }

                auto_fields = {
                    "lastupdated": {
                        "type": ["null", "integer"]
                    },
                    "idhash": {
                        "type": ["null", "integer"]
                    },
                    "lastuseragent": {
                        "type": ["null", "string"]
                    },
                    "lastmetadataupdate_agent": {
                        "type": ["null", "integer"]
                    }
                }
                for key in body['auto']:
                    auto_fields[key] = {
                        "type": ["null", self.get_valid_type(body['auto'][key]['Type'])]
                    }
                full_schema['properties']['metadata']['properties']['auto']['properties'] = auto_fields
                full_schema['properties']['metadata']['properties']['auto__323232']['properties'] = auto_fields

                full_schema = self.build_schema(full_schema, body)
                self.json_schema = full_schema
            except requests.exceptions.RequestException:
                self.json_schema = base_schema
        return self.json_schema

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping[str, Any]]:
        source = {
            "visitors": {
                "identified": True
            }
        }
        return self.build_request_body("visitor-list", source, next_page_token)


class Accounts(PendoAggregationStream):
    primary_key = "accountId"

    name = "Accounts"

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is None:
            base_schema = super().get_json_schema()
            url = f"{PendoPythonStream.url_base}metadata/schema/account"
            auth_headers = self.authenticator.get_auth_header()
            try:
                session = requests.get(url, headers=auth_headers)
                body = session.json()

                full_schema = base_schema
                full_schema['properties']['metadata']['properties']['auto__323232'] = {
                    "type": ["null", "object"]
                }

                auto_fields = {
                    "lastupdated": {
                        "type": ["null", "integer"]
                    },
                    "idhash": {
                        "type": ["null", "integer"]
                    }
                }
                for key in body['auto']:
                    auto_fields[key] = {
                        "type": ["null", self.get_valid_type(body['auto'][key]['Type'])]
                    }
                full_schema['properties']['metadata']['properties']['auto']['properties'] = auto_fields
                full_schema['properties']['metadata']['properties']['auto__323232']['properties'] = auto_fields

                full_schema = self.build_schema(full_schema, body)
                self.json_schema = full_schema
            except requests.exceptions.RequestException:
                self.json_schema = base_schema
        return self.json_schema

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping[str, Any]]:
        source = {"accounts": {}}
        return self.build_request_body("account-list", source, next_page_token)
