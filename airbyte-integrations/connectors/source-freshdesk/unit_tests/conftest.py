#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest
from requests.auth import HTTPBasicAuth
from source_freshdesk.source import SourceFreshdesk


@pytest.fixture(name="config")
def config_fixture():
    return {"domain": "test.freshdesk.com", "api_key": "secret_api_key", "requests_per_minute": 50, "start_date": "2002-02-10T22:21:44Z"}


@pytest.fixture(name="authenticator")
def authenticator_fixture(config):
    return HTTPBasicAuth(username=config["api_key"], password="unused_with_api_key")


def find_stream(stream_name, config):
    streams = SourceFreshdesk().streams(config=config)

    # cache should be disabled once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513
    for stream in streams:
        stream.retriever.requester.use_cache = True

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")
