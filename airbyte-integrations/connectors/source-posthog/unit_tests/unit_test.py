#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.logger import AirbyteLogger
from source_posthog import SourcePosthog


def test_client_wrong_credentials():
    source = SourcePosthog()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"api_key": "blahblah"})
    assert not status
