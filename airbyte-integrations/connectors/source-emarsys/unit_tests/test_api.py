import io
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
import pytz
import requests
from source_emarsys.api import EmarsysApi

USERNAME = "emarsys_user"
PASSWORD = "secret"


def no_sleep(seconds):
    pass


@pytest.fixture
def api():
    return EmarsysApi(USERNAME, PASSWORD)


def test_get_wsse__return_pattern(api):
    pattern = r'UsernameToken Username="emarsys_user", PasswordDigest="[a-zA-Z0-9+=/]+", Nonce="[a-zA-Z0-9]+", Created="\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00"'
    wsse = api._get_wsse()
    assert re.match(pattern, wsse)


@patch("source_emarsys.api.time.sleep", return_value=None)
def test_handle_rate_limit__no_limit_header_do_nothing(mock_sleep, api):
    response = requests.Response()
    response.headers = {}
    api._handle_rate_limit(response)
    mock_sleep.assert_not_called()


@patch("source_emarsys.api.time.sleep", return_value=None)
def test_handle_rate_limit__reset_timestamp_in_past_do_nothing(mock_sleep, api):
    response = requests.Response()
    past_ts = str(int((datetime.utcnow() - timedelta(seconds=1)).timestamp()))
    response.headers = {"X-Ratelimit-Remaining": "0", "X-Ratelimit-Reset": past_ts}
    api._handle_rate_limit(response)
    mock_sleep.assert_not_called()


@patch("source_emarsys.api.time.sleep", return_value=None)
def test_handle_rate_limit__delay(mock_sleep, api):
    response = requests.Response()
    future_ts = str(int((datetime.utcnow() + timedelta(seconds=15)).replace(tzinfo=pytz.UTC).timestamp()))
    response.headers = {"X-Ratelimit-Remaining": "0", "X-Ratelimit-Reset": future_ts}
    api._handle_rate_limit(response)
    mock_sleep.assert_called_once()


@patch("source_emarsys.api.requests.request")
def test__request__headers(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    response.raw = '{"data": []}'
    mock_request.return_value = response
    api.request("url", "GET")
    mock_request.assert_called()

    _, _, kwargs = mock_request.mock_calls[0]
    headers = kwargs.get("headers")
    assert "X-WSSE" in headers
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


@patch("source_emarsys.api.EmarsysApi._handle_rate_limit", return_value=None)
@patch("source_emarsys.api.requests.request")
def test__request__call_handle_api_limit(mock_request, mock_handle, api):
    response = requests.Response()
    response.status_code = 200
    mock_request.return_value = response
    api.request("url", "GET")
    mock_handle.assert_called()


@pytest.mark.parametrize("status_code", (201, 300, 400, 100, 500))
@patch("source_emarsys.api.requests.request")
def test__request__check_status_code_raise(mock_request, status_code, api):
    response = requests.Response()
    response.status_code = status_code
    mock_request.return_value = response
    with pytest.raises(requests.HTTPError):
        api._request("url", "GET")


@patch("source_emarsys.api.requests.request")
def test_request__success(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    response.raw = io.BytesIO('{"data": []}'.encode())
    mock_request.return_value = response
    response = api.request("url", "GET")
    assert response.json() == {"data": []}


@pytest.mark.parametrize("status_code", (201, 300, 400, 100, 500))
@patch.object(EmarsysApi, "retry_factor", 0)
@patch("source_emarsys.api.requests.request")
def test_request__retry(mock_request, status_code, api):
    response = requests.Response()
    response.status_code = status_code
    mock_request.return_value = response
    with pytest.raises(requests.HTTPError):
        api.request("url", "GET")
    assert mock_request.call_count == 3


@patch("source_emarsys.api.requests.request")
def test_get(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    mock_request.return_value = response
    response = api.get("url")
    _, args, _ = mock_request.mock_calls[0]
    assert args[0] == "GET"
    assert args[1] == "url"


@patch("source_emarsys.api.requests.request")
def test_post(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    mock_request.return_value = response
    response = api.post("url")
    _, args, _ = mock_request.mock_calls[0]
    assert args[0] == "POST"
    assert args[1] == "url"


@patch("source_emarsys.api.requests.request")
def test_put(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    mock_request.return_value = response
    response = api.put("url")
    _, args, _ = mock_request.mock_calls[0]
    assert args[0] == "PUT"
    assert args[1] == "url"


@patch("source_emarsys.api.requests.request")
def test_delete(mock_request, api):
    response = requests.Response()
    response.status_code = 200
    mock_request.return_value = response
    response = api.delete("url")
    _, args, _ = mock_request.mock_calls[0]
    assert args[0] == "DELETE"
    assert args[1] == "url"
