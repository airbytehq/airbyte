#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from source_posthog import SourcePosthog

logger = logging.getLogger("airbyte")


def test_client_wrong_credentials():
    source = SourcePosthog()
    status, error = source.check_connection(logger=logger, config={"api_key": "blahblah", "start_date": "2021-01-01T00:00:00Z"})
    assert not status
