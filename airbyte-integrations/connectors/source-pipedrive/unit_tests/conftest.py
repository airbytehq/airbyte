#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from source_pipedrive.source import SourcePipedrive

replication_start_date = "2017-01-25T00:00:00Z"


@pytest.fixture
def config_oauth():
    return {
        "authorization": {
            "auth_type": "Client",
            "client_id": "6779ef20e75817b79602",
            "client_secret": "7607999ef26581e81726777b7b79f20e70e75602",
            "refresh_token": "refresh_token",
        },
        "replication_start_date": replication_start_date,
    }


@pytest.fixture
def config_token():
    return {
        "authorization": {
            "auth_type": "Token",
            "api_token": "api_token"
        },
        "replication_start_date": replication_start_date
    }


@pytest.fixture
def stream_kwargs(config_token):
    return {"authenticator": SourcePipedrive.get_authenticator(config_token)}


@pytest.fixture
def incremental_kwargs(config_token):
    return {
        "authenticator": SourcePipedrive.get_authenticator(config_token),
        "replication_start_date": pendulum.parse(config_token["replication_start_date"])
    }
