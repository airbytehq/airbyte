# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Integration tests require a real ComfyUI Cloud API key.
Set up secrets/config.json with your API key before running."""

import json

import pytest
from source_comfyui.source import SourceComfyUI


@pytest.fixture
def config():
    with open("secrets/config.json") as f:
        return json.load(f)


@pytest.mark.integration
def test_check_connection(config):
    source = SourceComfyUI()
    ok, error = source.check_connection(None, config)
    assert ok, f"Connection check failed: {error}"


@pytest.mark.integration
def test_discover(config):
    source = SourceComfyUI()
    catalog = source.discover(None, config)
    assert len(catalog.streams) == 6
