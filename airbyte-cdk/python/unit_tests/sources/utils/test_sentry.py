#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
from unittest import mock

from airbyte_cdk.sources.utils.sentry import AirbyteSentry


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
