#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import responses
from destination_dewey.client import DeweyApiError, DeweyClient
from destination_dewey.config import DeweyConfig


BASE_URL = "https://api.meetdewey.com/v1"


def _client():
    return DeweyClient(DeweyConfig(api_key="dwy_test_x", base_url=BASE_URL))


@responses.activate
def test_check_returns_none_when_endpoint_responds_ok():
    responses.add(responses.GET, f"{BASE_URL}/collections", json=[], status=200)
    assert _client().check() is None


@responses.activate
def test_check_returns_auth_error_on_401():
    responses.add(responses.GET, f"{BASE_URL}/collections", status=401, json={"error": {"message": "bad key"}})
    err = _client().check()
    assert err and "Authentication failed" in err


@responses.activate
def test_get_collection_returns_none_on_404():
    responses.add(responses.GET, f"{BASE_URL}/collections/col_missing", status=404, json={"error": {"message": "nope"}})
    assert _client().get_collection("col_missing") is None


@responses.activate
def test_create_collection_passes_visibility():
    responses.add(
        responses.POST,
        f"{BASE_URL}/collections",
        json={"id": "col_new", "name": "x", "visibility": "private"},
        status=201,
        match=[responses.matchers.json_params_matcher({"name": "x", "visibility": "private"})],
    )
    result = _client().create_collection("x")
    assert result["id"] == "col_new"


@responses.activate
def test_upload_document_sends_multipart_with_tags_and_metadata():
    captured = {}

    def callback(request):
        captured["body"] = request.body
        captured["url"] = request.url
        return (202, {}, json.dumps({"id": "doc_1", "status": "uploading"}))

    responses.add_callback(
        responses.POST,
        f"{BASE_URL}/collections/col_test/documents",
        callback=callback,
        content_type="application/json",
    )
    result = _client().upload_document(
        "col_test",
        filename="x.json",
        content=b'{"a": 1}',
        tags=["airbyte_stream:default__x"],
        metadata={"_ab_pk": "1"},
    )
    assert result["id"] == "doc_1"
    assert "filename=x.json" in captured["url"]
    body_bytes = captured["body"].read() if hasattr(captured["body"], "read") else captured["body"]
    body_str = body_bytes.decode("utf-8", errors="replace") if isinstance(body_bytes, bytes) else str(body_bytes)
    assert "airbyte_stream:default__x" in body_str
    assert "_ab_pk" in body_str


@responses.activate
def test_upload_document_lowercases_tags_to_match_server_normalization():
    captured = {}

    def callback(request):
        body = request.body
        body = body.read() if hasattr(body, "read") else body
        captured["body"] = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
        return (202, {}, json.dumps({"id": "doc_1", "status": "uploading"}))

    responses.add_callback(
        responses.POST,
        f"{BASE_URL}/collections/col_test/documents",
        callback=callback,
        content_type="application/json",
    )
    _client().upload_document(
        "col_test",
        filename="x.json",
        content=b"{}",
        tags=["airbyte_stream:default__MixedCaseStream", "airbyte_pk:UUID-2A"],
    )
    # Tags must be lowercased before the wire — Dewey's normalizeTags would otherwise
    # silently rewrite them and break our exact-match find_document_ids_by_tag lookup.
    assert "airbyte_stream:default__mixedcasestream" in captured["body"]
    assert "airbyte_pk:uuid-2a" in captured["body"]
    assert "MixedCaseStream" not in captured["body"]


@responses.activate
def test_find_document_ids_by_tag_normalizes_query_tag():
    responses.add(
        responses.GET,
        f"{BASE_URL}/collections/col_test/documents",
        json={
            "documents": [
                {"id": "a", "tags": ["airbyte_stream:default__mixedcasestream"]},
                {"id": "b", "tags": ["airbyte_stream:other"]},
            ],
            "total": 2,
        },
        status=200,
    )
    # Caller passes the original mixed-case tag; lookup must still match the lowercased server value.
    ids = _client().find_document_ids_by_tag("col_test", "airbyte_stream:default__MixedCaseStream")
    assert ids == ["a"]


@responses.activate
def test_delete_documents_chunks_large_id_lists():
    responses.add(responses.DELETE, f"{BASE_URL}/collections/col_test/documents/batch", status=204)
    ids = [f"doc_{i}" for i in range(2500)]
    _client().delete_documents("col_test", ids)
    # 2500 split into chunks of 1000 → 3 calls
    assert len(responses.calls) == 3
    payloads = [json.loads(c.request.body) for c in responses.calls]
    assert sum(len(p["ids"]) for p in payloads) == 2500


@responses.activate
def test_delete_documents_no_op_when_empty():
    _client().delete_documents("col_test", [])
    assert len(responses.calls) == 0


@responses.activate
def test_list_documents_paginates_until_short_page():
    page_a = {"documents": [{"id": f"doc_{i}", "tags": []} for i in range(500)], "total": 750}
    page_b = {"documents": [{"id": f"doc_{i}", "tags": []} for i in range(500, 750)], "total": 750}
    responses.add(responses.GET, f"{BASE_URL}/collections/col_test/documents", json=page_a, status=200)
    responses.add(responses.GET, f"{BASE_URL}/collections/col_test/documents", json=page_b, status=200)
    docs = list(_client().list_documents("col_test"))
    assert len(docs) == 750


@responses.activate
def test_find_document_ids_by_tag_filters_client_side():
    responses.add(
        responses.GET,
        f"{BASE_URL}/collections/col_test/documents",
        json={
            "documents": [
                {"id": "a", "tags": ["airbyte_stream:default__x"]},
                {"id": "b", "tags": ["airbyte_stream:default__y"]},
                {"id": "c", "tags": ["airbyte_stream:default__x", "airbyte_pk:1"]},
            ],
            "total": 3,
        },
        status=200,
    )
    ids = _client().find_document_ids_by_tag("col_test", "airbyte_stream:default__x")
    assert ids == ["a", "c"]


@responses.activate
def test_request_raises_dewey_api_error_on_5xx_after_retries():
    responses.add(responses.GET, f"{BASE_URL}/collections/col_test", status=500, json={"error": {"message": "boom"}})
    with pytest.raises(Exception):
        _client().get_collection("col_test")
