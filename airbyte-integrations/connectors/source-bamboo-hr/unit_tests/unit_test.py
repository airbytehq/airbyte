#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status
from source_bamboo_hr.source import EmployeesDirectoryStream, SourceBambooHr


@pytest.fixture
def config():
    return {"api_key": "foo", "subdomain": "bar", "authenticator": "baz" }

def test_source_bamboo_hr_client_wrong_credentials():
    source = SourceBambooHr()
    result = source.check(logger=AirbyteLogger, config={"subdomain": "test", "api_key": "blah-blah"})
    assert result.status == Status.FAILED

def test_employees_directory_stream_url_base(config):
    stream = EmployeesDirectoryStream(config)
    assert stream.url_base == "https://api.bamboohr.com/api/gateway.php/bar/v1/"
