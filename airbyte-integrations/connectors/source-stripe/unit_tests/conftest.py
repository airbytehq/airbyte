#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import pytest
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.test.state_builder import StateBuilder

os.environ["CACHE_DISABLED"] = "true"
os.environ["DEPLOYMENT_MODE"] = "testing"


@pytest.fixture(name="config")
def config_fixture():
    config = {"client_secret": "sk_test(live)_<secret>", "account_id": "<account_id>", "start_date": "2020-05-01T00:00:00Z"}
    return config


@pytest.fixture(name="stream_args")
def stream_args_fixture():
    authenticator = TokenAuthenticator("sk_test(live)_<secret>")
    args = {
        "authenticator": authenticator,
        "account_id": "<account_id>",
        "start_date": 1588315041,
        "slice_range": 365,
    }
    return args


@pytest.fixture(name="incremental_stream_args")
def incremental_args_fixture(stream_args):
    return {"lookback_window_days": 14, **stream_args}


@pytest.fixture()
def stream_by_name(config):
    # use local import in favour of global because we need to make imports after setting the env variables
    from source_stripe.source import SourceStripe

    def mocker(stream_name, source_config=config):
        source = SourceStripe(None, source_config, StateBuilder().build())
        streams = source.streams(source_config)
        for stream in streams:
            if stream.name == stream_name:
                if isinstance(stream, StreamFacade):
                    # to avoid breaking changes for tests, we will return the legacy test. Tests that would be affected by not having this
                    # would probably need to be moved to integration tests or unit tests
                    return stream._legacy_stream
                return stream

    return mocker
