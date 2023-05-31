import json
import pytest
import requests

from unittest.mock import call, patch

from airbyte_cdk.sources.declarative.models.declarative_component_schema import ApiKeyAuthenticator, DeclarativeStream, DpathExtractor, HttpRequester, RecordSelector, SimpleRetriever
from airbyte_cdk.models import AirbyteMessage, SyncMode
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.http import HttpStream

class TestRequester:
    # TODO: I think this can be done by patching _send_request
    def test_read_no_setup(self):

        config = {}
        parameters = {}
        stream_name = "stream_name"
        primary_key = "id"
        field_path = ["data"]
        api_key = "api_key"
        url_base = "https://api.airbyte.io"
        path = "v1/endpoint"
        cursor_field = None
        api_key_header = "api_key"
        request_body_json = {}
        request_headers = {}
        expected_request_headers = {"User-Agent": "python-requests/2.28.2",
                           "Accept-Encoding": "gzip, deflate",
                            "Accept": "*/*",
                                    "Connection": "keep-alive",
                           "api_key": "api_key"}
        request_parameters = {}
        authenticator = ApiKeyAuthenticator(
            type="ApiKeyAuthenticator",
            api_token=api_key,
            header=api_key_header
        )

        expected_requests = [
        ]
        expected_records = [{"id": 0, "field": "valueA"}, {"id": 1, "field": "valueB"}]

        components = DeclarativeStream(
            type="DeclarativeStream",
            name=stream_name,
            config=config,
            parameters=parameters,
            retriever=SimpleRetriever(
                type="SimpleRetriever",
                parameters=parameters,
                config=config,
                record_selector=RecordSelector(
                    type="RecordSelector",
                    extractor=DpathExtractor(
                        type="DpathExtractor",
                        field_path=field_path,
                        config=config,
                        parameters=parameters,
                    )
                ),
                requester=HttpRequester(
                    type="HttpRequester",
                    url_base=url_base,
                    path=path,
                    authenticator=authenticator,
                    request_body_json=request_body_json,
                    request_headers=request_headers,
                    request_parameters=request_parameters
                )
            ),
        ).dict()

        requests.PreparedRequest.__repr__ = (
            lambda self: (
            json.dumps({"url": self.url,"headers":{**self.headers},"body":self.body}))
        )
        
        requests.PreparedRequest.__eq__ = lambda self, other: self.__repr__() == other.__repr__()

        requests.PreparedRequest.__hash__ = lambda self: hash(self.__repr__())

        stream = ModelToComponentFactory().create_component(DeclarativeStream, components, config)

        pages = (_create_page("https://api.airbyte.io/v1/endpoint",
                              request_headers,
                              request_body_json==request_body_json,
                              response_body={"data": [{"id": 0, "field": "valueA"}, {"id": 1, "field": "valueB"}],"_metadata": {"next": "next"}}), )

        response = (_create_response({"data": [{"id": 0, "field": "valueA"}, {"id": 1, "field": "valueB"}],"_metadata": {"next": "next"}}), )

        expected_calls = [
            call(_create_request("https://api.airbyte.io/v1/endpoint", expected_request_headers, request_body_json))
        ]

        with patch.object(HttpStream, "_actually_send_request", side_effect=response) as mock_http_stream:
            output_records_and_messages = stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=cursor_field)
                
            output_records = [ message for message in output_records_and_messages if isinstance(message, dict) ]

            assert expected_records == output_records
            mock_http_stream.assert_has_calls(expected_calls)

def _create_page(full_url, headers, request_body_json, response_body):
    return (_create_request(full_url, headers, request_body_json),
            _create_response(response_body))

def _create_request(full_url, headers, json_body):
    return requests.Request('GET', full_url, headers=headers, json=json_body if json_body else None).prepare()


def _create_response(body):
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(body).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    response.iter_content = lambda: response._content
    return response