import pytest
from unittest.mock import MagicMock, patch
from http import HTTPStatus
from source_google_directory_v2.source import GoogleDirectoryV2Stream


@pytest.fixture
def mock_credentials():
    return MagicMock()


class TestStream(GoogleDirectoryV2Stream):
    primary_key = "test_id"

    def path(self, **kwargs):
        return "test"


def test_base_stream(mock_credentials):
    mock_service = MagicMock()
    mock_build = MagicMock(return_value=mock_service)
    with patch('source_pulse_google_directory.source.build', mock_build):
        stream = TestStream(credentials=mock_credentials)
        assert stream.service == mock_service


def test_next_page_token(mock_credentials):
    stream = TestStream(credentials=mock_credentials)
    response = MagicMock()
    assert stream.next_page_token(response) is None


def test_parse_response(mock_credentials):
    stream = TestStream(credentials=mock_credentials)
    response = MagicMock()
    assert list(stream.parse_response(response)) == []


def test_request_headers(mock_credentials):
    stream = TestStream(credentials=mock_credentials)
    inputs = {"stream_state": None, "stream_slice": None, "next_page_token": None}
    assert stream.request_headers(**inputs) == {}


def test_http_method(mock_credentials):
    stream = TestStream(credentials=mock_credentials)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(mock_credentials, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = TestStream(credentials=mock_credentials)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(mock_credentials):
    response_mock = MagicMock()
    stream = TestStream(credentials=mock_credentials)
    assert stream.backoff_time(response_mock) is None
