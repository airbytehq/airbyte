#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import unittest
from unittest.mock import MagicMock, call, patch

import requests
from destination_vectara.client import VectaraClient


CONFIG = {
    "oauth2": {"client_id": "myclientid", "client_secret": "myclientsecret"},
    "corpus_name": "my corpus",
    "customer_id": "123456",
    "text_fields": [],
    "metadata_fields": [],
    "title_field": "",
}


def _response(status_code=200, json_body=None):
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.content = b"" if json_body is None else json.dumps(json_body).encode()
    response.json.return_value = json_body
    if status_code >= 400:
        error = requests.exceptions.HTTPError(response=response)
        response.raise_for_status.side_effect = error
    else:
        response.raise_for_status.return_value = None
    return response


class TestVectaraClient(unittest.TestCase):
    def _mock_responses(self, mock_request, responses):
        mock_request.side_effect = [_response(200, {"access_token": "token", "expires_in": 3600})] + responses

    @patch("destination_vectara.client.requests.request")
    def test_check_uses_existing_corpus(self, mock_request):
        self._mock_responses(mock_request, [_response(200, {"corpora": [{"key": "my-corpus", "name": "my corpus"}], "metadata": {}})])

        client = VectaraClient(CONFIG)

        assert client.corpus_key == "my-corpus"
        auth_call, list_call = mock_request.call_args_list
        assert auth_call == call(
            method="POST",
            url="https://auth.vectara.com/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials", "client_id": "myclientid", "client_secret": "myclientsecret"},
        )
        assert list_call.kwargs["method"] == "GET"
        assert list_call.kwargs["url"] == "https://api.vectara.io/v2/corpora"
        assert list_call.kwargs["params"] == {"limit": 100, "filter": "my corpus"}
        assert list_call.kwargs["headers"]["Authorization"] == "Bearer token"

    @patch("destination_vectara.client.requests.request")
    def test_check_creates_missing_corpus(self, mock_request):
        self._mock_responses(
            mock_request,
            [
                _response(200, {"corpora": [{"key": "other", "name": "other corpus"}], "metadata": {}}),
                _response(201, {"key": "my_corpus", "name": "my corpus"}),
            ],
        )

        client = VectaraClient(CONFIG)

        assert client.corpus_key == "my_corpus"
        create_call = mock_request.call_args_list[2]
        assert create_call.kwargs["method"] == "POST"
        assert create_call.kwargs["url"] == "https://api.vectara.io/v2/corpora"
        assert json.loads(create_call.kwargs["data"]) == {
            "key": "my_corpus",
            "name": "my corpus",
            "filter_attributes": [{"name": "_ab_stream", "level": "document", "type": "text", "indexed": True}],
        }

    @patch("destination_vectara.client.requests.request")
    def test_check_fails_with_multiple_corpora(self, mock_request):
        list_response = {"corpora": [{"key": "a", "name": "my corpus"}, {"key": "b", "name": "my corpus"}], "metadata": {}}
        # check() runs once in the constructor and once more explicitly below
        token_response = {"access_token": "token", "expires_in": 3600}
        mock_request.side_effect = [
            _response(200, token_response),
            _response(200, list_response),
            _response(200, token_response),
            _response(200, list_response),
        ]

        client = VectaraClient(CONFIG)

        assert client.corpus_key is None
        assert client.check() == "Multiple Corpora exist with name my corpus"

    @patch("destination_vectara.client.requests.request")
    def test_check_fails_with_invalid_credentials(self, mock_request):
        mock_request.return_value = _response(401, {"error": "invalid_client"})

        client = VectaraClient(CONFIG)

        assert client.check() == "Unable to get JWT Token. Confirm your Client ID and Client Secret."

    @patch("destination_vectara.client.requests.request")
    def test_index_document(self, mock_request):
        self._mock_responses(
            mock_request,
            [
                _response(200, {"corpora": [{"key": "my-corpus", "name": "my corpus"}], "metadata": {}}),
                _response(201, {"id": "doc-1"}),
            ],
        )
        client = VectaraClient(CONFIG)

        client.index_document(
            ({"text": "hello", "_ab_stream": "None_mystream"}, {"_ab_stream": "None_mystream", "tags": ["a"]}, "title", "doc-1")
        )

        index_call = mock_request.call_args_list[2]
        assert index_call.kwargs["method"] == "POST"
        assert index_call.kwargs["url"] == "https://api.vectara.io/v2/corpora/my-corpus/documents"
        assert json.loads(index_call.kwargs["data"]) == {
            "id": "doc-1",
            "type": "structured",
            "title": "title",
            "metadata": {"_ab_stream": "None_mystream", "tags": '["a"]'},
            "sections": [{"text": "text: hello"}],
        }

    @patch("destination_vectara.client.requests.request")
    def test_index_document_ignores_already_existing_document(self, mock_request):
        self._mock_responses(
            mock_request,
            [
                _response(200, {"corpora": [{"key": "my-corpus", "name": "my corpus"}], "metadata": {}}),
                _response(409, {"messages": ["The document already exists"]}),
            ],
        )
        client = VectaraClient(CONFIG)

        assert client.index_document(({"text": "hello"}, {}, "title", "doc-1")) is None

    @patch("destination_vectara.client.requests.request")
    def test_delete_doc_by_metadata(self, mock_request):
        self._mock_responses(
            mock_request,
            [
                _response(200, {"corpora": [{"key": "my-corpus", "name": "my corpus"}], "metadata": {}}),
                _response(200, {"documents": [{"id": "doc 1"}], "metadata": {"page_key": "next"}}),
                _response(200, {"documents": [{"id": "doc-2"}], "metadata": {}}),
                _response(204),
                _response(404, {"messages": ["Document not found"]}),
            ],
        )
        client = VectaraClient(CONFIG)

        client.delete_doc_by_metadata(metadata_field_name="_ab_stream", metadata_field_values=["None_mystream"])

        list_calls = mock_request.call_args_list[2:4]
        assert list_calls[0].kwargs["method"] == "GET"
        assert list_calls[0].kwargs["url"] == "https://api.vectara.io/v2/corpora/my-corpus/documents"
        assert list_calls[0].kwargs["params"] == {"limit": 1000, "metadata_filter": "doc._ab_stream = 'None_mystream'"}
        assert list_calls[1].kwargs["params"]["page_key"] == "next"
        delete_calls = mock_request.call_args_list[4:]
        assert [c.kwargs["method"] for c in delete_calls] == ["DELETE", "DELETE"]
        assert [c.kwargs["url"] for c in delete_calls] == [
            "https://api.vectara.io/v2/corpora/my-corpus/documents/doc%201",
            "https://api.vectara.io/v2/corpora/my-corpus/documents/doc-2",
        ]

    def test_corpus_key_from_name(self):
        assert VectaraClient._corpus_key_from_name("my corpus/v2") == "my_corpus_v2"
        assert len(VectaraClient._corpus_key_from_name("x" * 80)) == 50
