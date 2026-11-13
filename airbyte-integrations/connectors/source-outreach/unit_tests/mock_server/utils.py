# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Optional

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source

from .config import ConfigBuilder
from .request_builder import OutreachRequestBuilder
from .response_builder import token_response


def given_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(OutreachRequestBuilder.token_request(), token_response())


def read_stream(
    stream_name: str,
    sync_mode: SyncMode,
    config: Optional[dict[str, Any]] = None,
    state: Optional[list] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    config = config or ConfigBuilder().build()
    state = state if state is not None else StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(build_source(config, state), config, catalog, state, expecting_exception=expecting_exception)


def record_ids(output: EntrypointOutput) -> list[Any]:
    return [record.record.data["id"] for record in output.records]


def stream_state(output: EntrypointOutput) -> dict[str, Any]:
    return output.most_recent_state.stream_state.__dict__
