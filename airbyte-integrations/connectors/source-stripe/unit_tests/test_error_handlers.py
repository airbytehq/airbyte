#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List

from conftest import get_source
from integration.config import ConfigBuilder


def _resolved_definitions() -> Dict[str, Any]:
    return get_source(ConfigBuilder().build()).resolved_manifest["definitions"]


def _walk_error_handlers(node: Any) -> List[Dict[str, Any]]:
    handlers: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        if isinstance(node.get("error_handler"), dict):
            handlers.append(node["error_handler"])
        for value in node.values():
            handlers.extend(_walk_error_handlers(value))
    elif isinstance(node, list):
        for value in node:
            handlers.extend(_walk_error_handlers(value))
    return handlers


def _ignored_codes(error_handler: Dict[str, Any]) -> List[int]:
    return [
        code
        for response_filter in error_handler["response_filters"]
        if response_filter["action"] == "IGNORE"
        for code in response_filter["http_codes"]
    ]


def test_every_error_handler_is_a_single_default_error_handler() -> None:
    handlers = _walk_error_handlers(_resolved_definitions())
    assert handlers
    assert {handler["type"] for handler in handlers} == {"DefaultErrorHandler"}


def test_base_requester_ignores_403_400_and_404() -> None:
    error_handler = _resolved_definitions()["base_requester"]["error_handler"]
    assert _ignored_codes(error_handler) == [403, 400, 404]


def test_bank_accounts_full_refresh_requester_ignores_403_and_404_but_not_400() -> None:
    requester = _resolved_definitions()["streams"]["bank_accounts"]["full_refresh_stream"]["retriever"]["requester"]
    assert _ignored_codes(requester["error_handler"]) == [403, 404]
