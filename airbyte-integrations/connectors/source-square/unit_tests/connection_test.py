#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.logger import AirbyteLogger
from source_square.source import SourceSquare


def test_source_wrong_credentials():
    source = SourceSquare()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"api_key": "wrong.api.key", "is_sandbox": True})
    assert not status
