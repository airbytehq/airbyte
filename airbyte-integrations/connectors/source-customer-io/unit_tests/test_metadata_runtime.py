# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-customer-io` runtime metadata."""

import re
from pathlib import Path


_CONNECTOR_ROOT = Path(__file__).parent.parent


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    assert match is not None, f"pattern not found: {pattern}"
    return match.group(1)


def test_source_declarative_manifest_image_matches_locked_cdk_version():
    """The runtime SDM image version matches the unit test CDK lockfile version."""
    metadata = (_CONNECTOR_ROOT / "metadata.yaml").read_text()
    poetry_lock = (_CONNECTOR_ROOT / "unit_tests" / "poetry.lock").read_text()

    runtime_version = _extract(r"source-declarative-manifest:([^@\s]+)@sha256:[0-9a-f]{64}", metadata)
    locked_cdk_version = _extract(r'name = "airbyte-cdk"\nversion = "([^"]+)"', poetry_lock)

    assert runtime_version == locked_cdk_version
