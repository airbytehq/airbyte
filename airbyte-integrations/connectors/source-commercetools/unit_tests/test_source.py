# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path

from source_commercetools.source import SourceCommercetools


def _sample_config():
    return json.loads(Path("integration_tests/sample_config.json").read_text())


def test_spec():
    spec = SourceCommercetools().spec(logging.getLogger("airbyte"))

    assert set(spec.connectionSpecification["required"]) == {
        "region",
        "host",
        "start_date",
        "project_key",
        "client_id",
        "client_secret",
    }


def test_streams():
    streams = SourceCommercetools().streams(_sample_config())

    assert {stream.name for stream in streams} == {
        "customers",
        "discount_codes",
        "orders",
        "payments",
        "products",
    }
