# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Integration tests require a real ComfyUI Cloud API key.
Set up secrets/config.json with your API key before running."""

import json
from pathlib import Path

import pytest
from source_comfyui.source import SourceComfyUI


CONFIG_PATH = Path("secrets/config.json")
skip_no_creds = pytest.mark.skipif(not CONFIG_PATH.exists(), reason="No secrets/config.json")


@pytest.fixture
def config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


@skip_no_creds
@pytest.mark.integration
def test_check_connection(config):
    source = SourceComfyUI()
    ok, error = source.check_connection(None, config)
    assert ok, f"Connection check failed: {error}"


@skip_no_creds
@pytest.mark.integration
def test_discover(config):
    source = SourceComfyUI()
    catalog = source.discover(None, config)
    assert len(catalog.streams) == 6
