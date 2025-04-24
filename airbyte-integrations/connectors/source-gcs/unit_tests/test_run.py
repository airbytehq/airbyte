# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import pytest
from common import catalog_path, config_path
from source_gcs.run import run

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def test_run_with_non_existing_config():
    with patch("sys.argv", ["", "check", "--config", "non_existing.json"]):
        assert run() is None


def test_run_with_invalid_config():
    with patch(
        "sys.argv",
        ["", "read", "--config", f"{config_path()}/config_bad_encoding.json", "--catalog", f"{catalog_path()}/catalog_bad_encoding.json"],
    ):
        with pytest.raises(AirbyteTracedException):
            run()
