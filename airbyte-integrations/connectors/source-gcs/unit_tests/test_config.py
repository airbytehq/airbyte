# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from os import write

from source_gcs import Config


def test_documentation_url():
    assert "https" in Config.documentation_url()
