# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Any, Dict, Iterator, List

import yaml


def _error_handlers(value: Any) -> Iterator[Dict[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "error_handler":
                yield child
            yield from _error_handlers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _error_handlers(child)


def test_manifest_uses_only_default_error_handlers() -> None:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    handlers: List[Dict[str, Any]] = list(_error_handlers(manifest))

    assert handlers
    assert all(handler.get("type") == "DefaultErrorHandler" for handler in handlers)
