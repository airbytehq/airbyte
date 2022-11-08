#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator
from source_klarna import SourceKlarna
from source_klarna.source import KlarnaStream


@pytest.fixture(name="source_klarna")
def get_source_klarna():
    return SourceKlarna()


@pytest.fixture(name="klarna_config")
def get_klarna_config():
    return dict(playground=False, region="eu", username="user", password="password")


@pytest.fixture(name="klarna_stream")
def get_klarna_stream(klarna_config):
    return KlarnaStream(authenticator=BasicHttpAuthenticator("", ""), **klarna_config)
