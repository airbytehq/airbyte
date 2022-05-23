import io
import json
from unittest.mock import patch

import pytest
import requests
from source_emarsys.client import EmarsysClient


def make_response(status_code, data=None, headers=None):
    response = requests.Response()
    response.status_code = status_code
    response.headers = headers or {}
    if isinstance(data, (list, tuple, dict)):
        _data = json.dumps({"data": data})
        response.raw = io.BytesIO(_data.encode())
    return response


@pytest.fixture
def client():
    return EmarsysClient("username", "secret")


@patch("source_emarsys.api.requests.request")
def test_get__return_data(mock_request, client):
    mock_request.return_value = make_response(200, [1, 2])
    data = client.get("url")
    assert data == [1, 2]


def test__params_pagination__output(client):
    params = client._params_pagination({}, 100)
    assert params["offset"] == 100
    assert params["limit"] == client.limit


@patch("source_emarsys.api.requests.request")
def test_fetch_all__no_result(mock_request, client):
    response = make_response(200, [])
    # Client should make only 1 request. If it makes the 2nd call
    # an exception will be thrown
    mock_request.side_effect = [response, Exception()]
    data = list(client.fetch_all("url"))
    assert mock_request.call_count == 1
    assert data == []


@patch("source_emarsys.api.requests.request")
def test_fetch_all__one_page(mock_request, client):
    mock_request.side_effect = [make_response(200, [1, 2]), make_response(200, [])]
    data = list(client.fetch_all("url"))
    assert mock_request.call_count == 2
    assert data == [1, 2]
    _, _, kwargs = mock_request.mock_calls[1]
    assert kwargs["params"]["offset"] == 2


@patch("source_emarsys.api.requests.request")
def test_fetch_all__multi_pages(mock_request, client):
    mock_request.side_effect = [
        make_response(200, [1, 2]),
        make_response(200, [3, 4, 5]),
        make_response(200, [6]),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.fetch_all("url"))
    assert mock_request.call_count == 4
    assert data == [1, 2, 3, 4, 5, 6]
    _, _, kwargs = mock_request.mock_calls[-1]
    assert kwargs["params"]["offset"] == 6


@patch("source_emarsys.api.requests.request")
def test_list_fields(mock_request, client):
    mock_data = [{"id": 1, "name": "email"}, {"id": 2, "name": "address"}]
    mock_request.side_effect = [
        make_response(200, mock_data),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.list_fields())
    assert mock_request.call_count == 2
    _, args, _ = mock_request.mock_calls[0]
    assert "v2/field" in args[1]
    assert data == mock_data


@patch("source_emarsys.api.requests.request")
def test_list_contact_lists(mock_request, client):
    mock_data = [{"id": 1, "name": "list A"}, {"id": 2, "name": "List B"}]
    mock_request.side_effect = [
        make_response(200, mock_data),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.list_contact_lists())
    assert mock_request.call_count == 2
    _, args, _ = mock_request.mock_calls[0]
    assert "v2/contactlist" in args[1]
    assert data == mock_data


@patch("source_emarsys.api.requests.request")
def test_list_contacts_in_list(mock_request, client):
    list_id = 123
    mock_data = [{"id": 1}, {"id": 2}]
    mock_request.side_effect = [
        make_response(200, mock_data),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.list_contacts_in_list(list_id))
    assert mock_request.call_count == 2
    _, args, _ = mock_request.mock_calls[0]
    assert f"v2/contactlist/{list_id}" in args[1]
    assert data == mock_data


@patch("source_emarsys.api.requests.request")
def test_list_contact_data_in_lists(mock_request, client):
    list_id = 123
    field_ids = [1, 2, 3, 4]
    mock_data = [{"id": 1}, {"id": 2}]
    mock_request.side_effect = [
        make_response(200, mock_data),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.list_contact_data_in_list(list_id, field_ids))
    assert mock_request.call_count == 2
    _, args, kwargs = mock_request.mock_calls[0]
    assert f"v2/contactlist/{list_id}/contacts/data" in args[1]
    assert data == mock_data
    assert kwargs["params"]["fields"] == "1,2,3,4"


@patch("source_emarsys.api.requests.request")
def test_list_segments(mock_request, client):
    mock_data = [{"id": 1}, {"id": 2}]
    mock_request.side_effect = [
        make_response(200, mock_data),
        make_response(200, []),
        make_response(200, []),
    ]
    data = list(client.list_segments())
    assert mock_request.call_count == 2
    _, args, _ = mock_request.mock_calls[0]
    assert "v2/filter" in args[1]
    assert data == mock_data
