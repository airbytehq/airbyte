
from unittest.mock import MagicMock, Mock

import pendulum
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
import pytest

from source_rakuten_rms import SourceRakutenRms

@pytest.fixture
def authenticator(token_config):
    return TokenAuthenticator(token_config["credentials"]["api_token"])

def get_stream_by_name(stream_name, config):
    streams = SourceRakutenRms().streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")