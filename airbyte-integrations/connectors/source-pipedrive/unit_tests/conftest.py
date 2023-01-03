#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest

replication_start_date = "2017-01-25T00:00:00Z"


@pytest.fixture(name="config_oauth")
def config_oauth():
    return {
        "authorization": {
            "auth_type": "Client",
            "client_id": "6779ef20e75817b79602",
            "client_secret": "7607999ef26581e81726777b7b79f20e70e75602",
            "refresh_token": "RjY2NjM5NzA2OWJjuE7c",
        },
        "replication_start_date": replication_start_date,
    }


@pytest.fixture(name="config_token")
def config_token():
    return {"authorization": {"auth_type": "Token", "api_token": "jBzsujyut9x0nzXB8vhGl"}, "replication_start_date": replication_start_date}


@pytest.fixture(name="config_incremental")
def config_incremental():
    return {"authenticator": {"api_token": "jBzsujyut9x0nzXB8vhGl"}, "replication_start_date": pendulum.parse(replication_start_date)}


@pytest.fixture(name="config_refresh")
def config_refresh():
    return {"authenticator": {"api_token": "jBzsujyut9x0nzXB8vhGl"}}
