#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from source_posthog import SourcePosthog

from airbyte_cdk.logger import AirbyteLogger


def test_client_wrong_credentials():
    source = SourcePosthog()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"api_key": "blahblah", "start_date": "2021-01-01T00:00:00Z"})
    assert not status
