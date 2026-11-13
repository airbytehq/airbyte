# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import datetime
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
CONFIG = {"api_key": "fake-api-key", "application_key": "fake-application-key", "site": "datadoghq.com"}


def get_source(
    config: Mapping[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
    catalog: ConfiguredAirbyteCatalog | None = None,
) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(
        path_to_yaml=str(MANIFEST_PATH),
        catalog=catalog,
        config=CONFIG if config is None else config,
        state=state,
    )


def read_stream(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    config: Mapping[str, Any] | None = None,
    state: list[AirbyteStateMessage] | None = None,
    expecting_error: bool = False,
) -> EntrypointOutput:
    """Read one stream. The caller mocks the HTTP responses."""
    config = CONFIG if config is None else config
    stream = ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode)
    catalog = CatalogBuilder().with_stream(stream).build()
    expected_outcome = ExpectedOutcome.EXPECT_EXCEPTION if expecting_error else ExpectedOutcome.EXPECT_SUCCESS
    return read(get_source(config, state, catalog), config, catalog, state, expected_outcome=expected_outcome)


def stream_errors(output: EntrypointOutput, stream_name: str) -> list[AirbyteErrorTraceMessage]:
    """The errors a read reported for one stream, without the summary error that closes a failed sync."""
    errors = [message.trace.error for message in output.errors]
    return [error for error in errors if error.stream_descriptor and error.stream_descriptor.name == stream_name]


def state_of(stream_name: str, stream_state: Mapping[str, Any]) -> list[AirbyteStateMessage]:
    return StateBuilder().with_stream_state(stream_name, dict(stream_state)).build()


def saved_state(output: EntrypointOutput) -> dict[str, Any]:
    """The last state a read saved."""
    return dict(output.most_recent_state.stream_state.__dict__)


@contextmanager
def now_is(moment: datetime.datetime) -> Iterator[None]:
    """Set the time the manifest's `now_utc` and `day_delta` macros read. Every other clock keeps running."""

    class _Datetime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None) -> datetime.datetime:
            return moment.astimezone(tz) if tz else moment.replace(tzinfo=None)

    clock = ModuleType("datetime")
    clock.__dict__.update(vars(datetime))
    clock.datetime = _Datetime
    with mock.patch("airbyte_cdk.sources.declarative.interpolation.macros.datetime", clock):
        yield
