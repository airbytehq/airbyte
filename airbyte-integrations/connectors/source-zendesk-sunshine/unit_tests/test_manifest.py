# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
with MANIFEST_PATH.open() as manifest_file:
    MANIFEST = yaml.safe_load(manifest_file)


@pytest.mark.parametrize("stream", MANIFEST["definitions"]["streams"].values(), ids=MANIFEST["definitions"]["streams"])
def test_requester_error_handler(stream: dict) -> None:
    error_handler = stream["retriever"]["requester"]["error_handler"]

    assert error_handler["type"] == "DefaultErrorHandler"
    assert error_handler["backoff_strategies"] == [{"type": "WaitTimeFromHeader", "header": "Retry-After"}]
