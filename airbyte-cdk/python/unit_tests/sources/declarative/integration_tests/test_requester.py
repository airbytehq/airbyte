import json
import pytest
import requests

from unittest.mock import call, patch

from airbyte_cdk.sources.declarative.models.declarative_component_schema import ApiKeyAuthenticator, DeclarativeStream, DefaultPaginator, DpathExtractor, HttpRequester, PageIncrement, RecordSelector, RequestOption, SimpleRetriever
from airbyte_cdk.models import AirbyteMessage, SyncMode
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.http import HttpStream

class TestRequester:
    def test_request_body_json_is_simple_dict(self):
        request_body_json = {"key": "value"}

        expected_requests = [
            _create_request("https://api.airbyte.io/v1/endpoint",
                            {},
                            {"key": "value"})
        ]
        responses = (_create_response({
            "data": [{"id": 0, "field": "valueA"},
                     {"id": 1, "field": "valueB"}],
            "_metadata": {"next": "next"}}), )
        expected_records = [{"id": 0, "field": "valueA"},
                            {"id": 1, "field": "valueB"}]

        stream = self._build(request_body_json=request_body_json)

        self._test(stream, expected_requests, responses, expected_records)

    def test_request_body_json_is_nested_dict(self):
        request_body_json = {"key": {"nested_key": "value"}, "another_key": "another_value"}

        expected_requests = [
            _create_request("https://api.airbyte.io/v1/endpoint",
                            {},
                            {"key": {"nested_key": "value"},"another_key": "another_value"})
        ]
        responses = (_create_response({
            "data": [{"id": 0, "field": "valueA"},
                     {"id": 1, "field": "valueB"}],
            "_metadata": {"next": "next"}}), )
        expected_records = [{"id": 0, "field": "valueA"},
                            {"id": 1, "field": "valueB"}]

        stream = self._build(request_body_json=request_body_json)

        self._test(stream, expected_requests, responses, expected_records)

    def test_request_headers_are_set(self):
        request_headers = {"header_key": "header_value"}

        expected_requests = [
            _create_request("https://api.airbyte.io/v1/endpoint",
                            {"header_key": "header_value"},
                            {})
        ]
        responses = (_create_response({
            "data": [{"id": 0, "field": "valueA"},
                     {"id": 1, "field": "valueB"}],
            "_metadata": {"next": "next"}}), )
        expected_records = [{"id": 0, "field": "valueA"},
                            {"id": 1, "field": "valueB"}]

        stream = self._build(request_headers=request_headers)

        self._test(stream, expected_requests, responses, expected_records)

    def test_request_parameters_are_set(self):
        request_parameters = {"key": "value"}

        expected_requests = [
            _create_request("https://api.airbyte.io/v1/endpoint?key=value",
                            {},
                            {})
        ]
        responses = (_create_response({
            "data": [{"id": 0, "field": "valueA"},
                     {"id": 1, "field": "valueB"}],
            "_metadata": {"next": "next"}}), )
        expected_records = [{"id": 0, "field": "valueA"},
                            {"id": 1, "field": "valueB"}]

        stream = self._build(request_parameters=request_parameters)

        self._test(stream, expected_requests, responses, expected_records)

    def test_page_count_pagination(self):
        page_size = 2
        paginator = DefaultPaginator(
            type="DefaultPaginator",
            pagination_strategy=PageIncrement(
                type="PageIncrement",
                page_size=page_size,
                start_from_page=1,
            ),
            page_size_option=RequestOption(type="RequestOption", field_name="page_size", inject_into="request_parameter"),
            page_token_option=RequestOption(type="RequestOption", field_name="page", inject_into="request_parameter")
        )

        expected_requests = [
            _create_request(f"https://api.airbyte.io/v1/endpoint?page_size={page_size}",
                            {},
                            {}),
            _create_request(f"https://api.airbyte.io/v1/endpoint?page=2&page_size={page_size}",
                            {},
                            {}),
        ]
        responses = (
            _create_response({
                "data": [{"id": 0, "field": "valueA"},
                     {"id": 1, "field": "valueB"}],
                "_metadata": {"next": "next"}}),
            _create_response({
                "data": [{"id": 2, "field": "valueC"}],
                "_metadata": {"next": "next"}}),
            )
        expected_records = [{"id": 0, "field": "valueA"},
                            {"id": 1, "field": "valueB"},
                            {"id": 2, "field": "valueC"}]

        stream = self._build(paginator=paginator)

        self._test(stream, expected_requests, responses, expected_records)

    def _build(self,
               *, 
               stream_name: str = "stream_name",
               field_path = ["data"],
               url_base = "https://api.airbyte.io",
               path = "v1/endpoint",
               authenticator = None,
               paginator = None,
               request_headers = {},
               request_parameters = {},
               request_body_json = {},
               config = {}):
        components = DeclarativeStream(
            type="DeclarativeStream",
            name=stream_name,
            config=config,
            parameters={},
            retriever=SimpleRetriever(
                type="SimpleRetriever",
                parameters={},
                config=config,
                paginator=paginator,
                record_selector=RecordSelector(
                    type="RecordSelector",
                    extractor=DpathExtractor(
                        type="DpathExtractor",
                        field_path=field_path,
                        config=config,
                        parameters={},
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
        return ModelToComponentFactory().create_component(DeclarativeStream, components, config)

    def _test(self, stream, expected_requests, responses, expected_records):
        requests.PreparedRequest.__repr__ = (
            # FIXME: need to check the headers and body!
            lambda self: (
            json.dumps({"url": self.url})
        ))
        
        requests.PreparedRequest.__eq__ = lambda self, other: json.loads(self.__repr__()) == json.loads(other.__repr__())

        requests.PreparedRequest.__hash__ = lambda self: hash(json.loads(self.__repr__()))

        expected_calls = [
            call(request) for request in expected_requests
        ]

        with patch.object(HttpStream, "_actually_send_request", side_effect=responses) as mock_http_stream:
            output_records_and_messages = stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None)
                
            output_records = [ message for message in output_records_and_messages if isinstance(message, dict) ]

            assert expected_records == output_records
            mock_http_stream.assert_has_calls(expected_calls)

def _create_request(full_url, additional_headers, json_body):
    base_headers = {
            "User-Agent": "python-requests/2.28.2",
                           "Accept-Encoding": "gzip, deflate",
                            "Accept": "*/*",
                            "Connection": "keep-alive"}
    all_headers = {**base_headers, **additional_headers}
    return requests.Request('GET', full_url, headers=all_headers, json=json_body).prepare()


def _create_response(body):
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(body).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    #response.iter_content = lambda: response._content
    return response