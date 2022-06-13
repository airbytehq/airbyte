#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
from dataclasses import dataclass
from logging import getLogger
from typing import List
from unittest import mock

import requests
from airbyte_cdk.sources.utils.sentry import AirbyteSentry
from sentry_sdk.transport import Transport


@mock.patch("airbyte_cdk.sources.utils.sentry.sentry_sdk")
def test_sentry_init_no_env(sentry_mock):
    assert AirbyteSentry.DSN_ENV_NAME not in os.environ
    AirbyteSentry.init("test_source")
    assert not sentry_mock.init.called
    assert not AirbyteSentry.sentry_enabled
    AirbyteSentry.set_tag("tagname", "value")
    assert not sentry_mock.set_tag.called
    AirbyteSentry.add_breadcrumb("msg", data={})
    assert not sentry_mock.add_breadcrumb.called

    with AirbyteSentry.start_transaction("name", "op"):
        assert not sentry_mock.start_transaction.called

    with AirbyteSentry.start_transaction_span("name", "op"):
        assert not sentry_mock.start_span.called


@mock.patch.dict(os.environ, {AirbyteSentry.DSN_ENV_NAME: "dsn"})
@mock.patch("airbyte_cdk.sources.utils.sentry.sentry_sdk")
def test_sentry_init(sentry_mock):
    AirbyteSentry.init("test_source")
    assert sentry_mock.init.called
    sentry_mock.set_tag.assert_any_call("source", "test_source")
    sentry_mock.set_tag.assert_any_call("run_id", mock.ANY)
    assert AirbyteSentry.sentry_enabled
    AirbyteSentry.set_tag("tagname", "value")
    assert sentry_mock.set_tag.called
    AirbyteSentry.add_breadcrumb("msg", data={})
    assert sentry_mock.add_breadcrumb.called
    with AirbyteSentry.start_transaction("name", "op"):
        assert sentry_mock.start_transaction.called

    with AirbyteSentry.start_transaction_span("name", "op"):
        assert sentry_mock.start_span.called


@dataclass
class TestTransport(Transport):
    secrets: List[str]
    # Sentry sdk wraps sending event with try except that would intercept
    # AssertionError exception resulting it would ignore assert directive.
    # Use this variable to check if test failed after sentry code executed.
    failed = None

    def capture_envelope(self, envelop):
        for s in self.secrets:
            for i in envelop.items:
                payload = json.dumps(i.payload.json)
                assert s not in payload

    def capture_event(self, event):
        if self.failed:
            return
        event = json.dumps(event)
        for s in self.secrets:
            if s in event:
                self.failed = f"{s} should not be in {event}"
                return


@mock.patch.dict(os.environ, {AirbyteSentry.DSN_ENV_NAME: "https://22222@222.ingest.sentry.io/111"})
def test_sentry_sensitive_info(httpserver):
    SECRET = "SOME_secret"
    UNEXPECTED_SECRET = "UnexEpectedSecret"
    SECRETS = [SECRET]
    transport = TestTransport(secrets=[*SECRETS, UNEXPECTED_SECRET])

    AirbyteSentry.init("test_source", transport=transport, secret_values=SECRETS)

    AirbyteSentry.add_breadcrumb("msg", {"crumb": SECRET})
    AirbyteSentry.set_context("my secret", {"api_key": SECRET})
    AirbyteSentry.capture_message(f"this is {SECRET}")
    AirbyteSentry.capture_message(f"Issue url http://localhost:{httpserver.port}/test?api_key={UNEXPECTED_SECRET}")
    AirbyteSentry.capture_message(f"Issue url http://localhost:{httpserver.port}/test?access_token={UNEXPECTED_SECRET}")
    AirbyteSentry.capture_message(f"Issue url http://localhost:{httpserver.port}/test?refresh_token={UNEXPECTED_SECRET}")
    AirbyteSentry.set_context("headers", {"Authorization": f"Bearer {UNEXPECTED_SECRET}"})
    getLogger("airbyte").info(f"this is {SECRET}")
    requests.get(
        f"http://localhost:{httpserver.port}/test?api_key={SECRET}",
        headers={"Authorization": f"Bearer {SECRET}"},
    ).text
    requests.get(
        f"http://localhost:{httpserver.port}/test?api_key={UNEXPECTED_SECRET}",
        headers={"Authorization": f"Bearer {UNEXPECTED_SECRET}"},
    ).text
    AirbyteSentry.capture_exception(Exception(f"Secret info: {SECRET}"))
    assert not transport.failed


@mock.patch.dict(os.environ, {AirbyteSentry.DSN_ENV_NAME: "https://22222@222.ingest.sentry.io/111"})
def test_sentry_sensitive_info_transactions(httpserver):
    SECRET = "SOME_secret"
    SECRETS = [SECRET]
    UNEXPECTED_SECRET = "UnexEpectedSecret"
    transport = TestTransport(secrets=[*SECRETS, UNEXPECTED_SECRET])
    AirbyteSentry.init("test_source", transport=transport, secret_values=SECRETS)

    AirbyteSentry.set_context("my secret", {"api_key": SECRET})
    AirbyteSentry.set_context("headers", {"Authorization": f"Bearer {UNEXPECTED_SECRET}"})
    with AirbyteSentry.start_transaction("name", "op"):
        with AirbyteSentry.start_transaction_span(
            "name", description=f"http://localhost:{httpserver.port}/test?api_key={UNEXPECTED_SECRET}"
        ):
            requests.get(
                f"http://localhost:{httpserver.port}/test?api_key={SECRET}",
                headers={"Authorization": f"Bearer {SECRET}"},
            ).text
    assert not transport.failed
