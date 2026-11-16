# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import threading
from datetime import timedelta
from unittest import TestCase

import requests
import yaml
from conftest import _YAML_FILE_PATH
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import OAuthAuthenticator as OAuthAuthenticatorModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import ACCESS_TOKEN, PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, read_streams, record_ids, stream_error


_EXPIRED_TOKEN_MESSAGE = (
    "Salesforce rejected the refresh token: it expired, was revoked, or went unused for 30 days. Create a new refresh token and "
    "update the source."
)


def _request(path: str = "v5/objects/campaigns", host: str = "pi.pardot.com") -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(path).with_host(host).with_any_query_params()


def _page(record_id: int) -> HttpResponse:
    return page_response([{"id": record_id, "updatedAt": "2026-03-01T09:00:00-08:00"}])


def _login_error(error: str, description: str) -> HttpResponse:
    return HttpResponse(body=json.dumps({"error": error, "error_description": description}), status_code=400)


def _manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


class _LoginsInFlight:
    """Counts the token requests sent and the most that were in flight at the same moment."""

    def __init__(self, hold_seconds: float) -> None:
        self._hold_seconds = hold_seconds
        self._lock = threading.Lock()
        self._now = 0
        self.most = 0
        self.total = 0

    def wrap(self, send):
        def tracked_send(session: requests.Session, request: requests.PreparedRequest, **kwargs) -> requests.Response:
            if "/services/oauth2/token" not in request.url:
                return send(session, request, **kwargs)
            with self._lock:
                self._now += 1
                self.total += 1
                self.most = max(self.most, self._now)
            try:
                # Holds the request open on the real clock, so a second token request sent meanwhile would overlap it.
                threading.Event().wait(self._hold_seconds)
                return send(session, request, **kwargs)
            finally:
                with self._lock:
                    self._now -= 1

        return tracked_send


class TestHosts(TestCase):
    @HttpMocker()
    def test_production_config_logs_in_at_login_salesforce_com_and_reads_from_pi_pardot_com(self, http_mocker: HttpMocker) -> None:
        login = login_request("login.salesforce.com")
        request = _request(host="pi.pardot.com").build()
        http_mocker.post(login, login_response())
        http_mocker.get(request, _page(1))

        output = read_stream("campaigns", config=ConfigBuilder().with_is_sandbox(False).build())

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_sandbox_config_logs_in_at_test_salesforce_com_and_reads_from_the_demo_host(self, http_mocker: HttpMocker) -> None:
        login = login_request("test.salesforce.com")
        request = _request(host="pi.demo.pardot.com").build()
        http_mocker.post(login, login_response())
        http_mocker.get(request, _page(1))

        output = read_stream("campaigns", config=ConfigBuilder().with_is_sandbox(True).build())

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_developer_edition_config_logs_in_at_login_salesforce_com_and_reads_from_the_demo_host(self, http_mocker: HttpMocker) -> None:
        login = login_request("login.salesforce.com")
        request = _request(host="pi.demo.pardot.com").build()
        http_mocker.post(login, login_response())
        http_mocker.get(request, _page(1))

        config = ConfigBuilder().with_is_sandbox(False).with_pardot_api_host("pi.demo.pardot.com").build()
        output = read_stream("campaigns", config=config)

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_an_explicit_api_host_wins_over_is_sandbox(self, http_mocker: HttpMocker) -> None:
        login = login_request("test.salesforce.com")
        request = _request(host="pi.pardot.com").build()
        http_mocker.post(login, login_response())
        http_mocker.get(request, _page(1))

        config = ConfigBuilder().with_is_sandbox(True).with_pardot_api_host("pi.pardot.com").build()
        output = read_stream("campaigns", config=config)

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)
        http_mocker.assert_number_of_calls(request, 1)


class TestLogin(TestCase):
    @HttpMocker()
    def test_each_stream_logs_in_for_itself(self, http_mocker: HttpMocker) -> None:
        # A pin, not a goal: the token is kept per stream. What the authenticator changes is that the logins never overlap.
        login = login_request()
        http_mocker.post(login, login_response())
        http_mocker.get(_request("v5/objects/campaigns").build(), _page(1))
        http_mocker.get(_request("v5/objects/lists").build(), _page(2))

        output = read_streams(["campaigns", "lists"], SyncMode.full_refresh)

        assert sorted(record_ids(output)) == [1, 2]
        http_mocker.assert_number_of_calls(login, 2)

    @HttpMocker()
    def test_expired_refresh_token_fails_as_a_configuration_error(self, http_mocker: HttpMocker) -> None:
        login = login_request()
        http_mocker.post(login, _login_error("invalid_grant", "expired access/refresh token"))

        error = stream_error(read_stream("campaigns", expecting_error=True))

        assert error.failure_type == FailureType.config_error
        assert error.message.startswith(_EXPIRED_TOKEN_MESSAGE)
        http_mocker.assert_number_of_calls(login, 1)

    @HttpMocker()
    def test_another_400_from_the_token_endpoint_is_not_a_configuration_error(self, http_mocker: HttpMocker) -> None:
        login = login_request()
        http_mocker.post(login, _login_error("invalid_client", "invalid client credentials"))

        error = stream_error(read_stream("campaigns", expecting_error=True))

        assert error.failure_type == FailureType.system_error
        http_mocker.assert_number_of_calls(login, 1)

    @HttpMocker()
    def test_token_request_already_being_processed_is_not_retried(self, http_mocker: HttpMocker) -> None:
        # A pin. Logins no longer overlap, which is what made Salesforce send this answer.
        login = login_request()
        http_mocker.post(login, _login_error("invalid_grant", "token request is already being processed"))

        error = stream_error(read_stream("campaigns", expecting_error=True))

        assert error.failure_type == FailureType.system_error
        http_mocker.assert_number_of_calls(login, 1)


def test_streams_read_concurrently_never_log_in_at_the_same_time() -> None:
    tracker = _LoginsInFlight(hold_seconds=0.02)
    streams = _manifest()["streams"]
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        for stream in streams:
            path = stream["retriever"]["requester"]["path"]
            if stream["name"] == "account":
                body = {"id": 1}
            elif stream["name"] == "email_clicks":
                body = {"result": {"emailClick": []}}
            else:
                body = {"nextPageToken": None, "nextPageUrl": None, "values": []}
            http_mocker.get(_request(path).build(), HttpResponse(body=json.dumps(body), status_code=200))
        # Wraps the mocker's own transport, and puts it back before the mocker restores the real one.
        mocked_send = requests.Session.send
        requests.Session.send = tracker.wrap(mocked_send)
        try:
            read_streams([stream["name"] for stream in streams], SyncMode.full_refresh)
        finally:
            requests.Session.send = mocked_send

    assert len(streams) == 33
    assert tracker.most == 1
    # A pin, not a goal: one login per stream read.
    assert tracker.total == 33


def test_a_token_without_expires_in_is_kept_one_hour() -> None:
    definition = _manifest()["definitions"]["base_requester"]["authenticator"]
    config = ConfigBuilder().build()
    with freeze_time("2026-06-01T00:00:00Z") as clock, HttpMocker() as http_mocker:
        login = login_request()
        http_mocker.post(login, login_response())
        authenticator = ModelToComponentFactory().create_component(OAuthAuthenticatorModel, definition, config=config)

        assert authenticator.get_access_token() == ACCESS_TOKEN
        clock.tick(delta=timedelta(seconds=3599))
        authenticator.get_access_token()
        http_mocker.assert_number_of_calls(login, 1)
        clock.tick(delta=timedelta(seconds=2))
        authenticator.get_access_token()
        http_mocker.assert_number_of_calls(login, 2)
