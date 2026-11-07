#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import yaml

from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler


def test_base_requester_uses_single_default_error_handler(manifest_path: Path) -> None:
    manifest = yaml.safe_load(manifest_path.read_text())
    requester = ModelToComponentFactory().create_component(
        model_type=HttpRequester,
        component_definition=manifest["definitions"]["base_requester"],
        config={"client_id": "id", "client_secret": "secret", "client_refresh_token_2": "rt"},
        name="test",
    )

    handler = requester.error_handler
    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert len(manifest["definitions"]["base_requester"]["error_handler"]["response_filters"]) == 9
    assert len(handler.backoff_strategies) == 1
    assert handler.backoff_strategies[0].backoff_time(None, attempt_count=0) == 5
    assert handler.backoff_strategies[0].backoff_time(None, attempt_count=2) == 20
