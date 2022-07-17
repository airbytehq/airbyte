#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

from source_square.source import SourceSquare


def test_source_wrong_credentials():
    source = SourceSquare()
    config = {
        "credentials": {"auth_type": "Apikey", "api_key": "bla"},
        "is_sandbox": True,
        "start_date": "2021-06-01",
        "include_deleted_objects": False,
    }
    status, error = source.check_connection(logger=logging.getLogger("airbyte"), config=config)
    assert not status
