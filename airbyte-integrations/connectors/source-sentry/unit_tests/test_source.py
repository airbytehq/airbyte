#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.logger import AirbyteLogger
from source_sentry.source import SourceSentry

def test_source_wrong_credentials():
    source = SourceSentry()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"auth_token": "test_auth_token"})
    assert not status
