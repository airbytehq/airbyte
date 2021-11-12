#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status
from source_bamboo_hr.source import SourceBambooHr


def test_client_wrong_credentials():
    source = SourceBambooHr()
    result = source.check(logger=AirbyteLogger, config={"subdomain": "test", "api_key": "blah-blah"})
    assert result.status == Status.FAILED
