# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

from source_chargebee.run import run


def test_run_with_non_existing_config():
    with patch("sys.argv", ["", "check", "--config", "resource/config/config.json"]):
        # A check failed message is expected because the test config doesn't have a valid API key. But this
        # still validates that we could instantiate the concurrent source correctly with the incoming args
        assert run() is None
