# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
from collections.abc import Callable, Iterable

import pytest
from _pytest.fixtures import SubRequest
from airbyte_protocol.models import AirbyteCatalog, AirbyteStream, Type  # type: ignore
from live_tests.commons.models import ExecutionResult

from .utils import fail_test_on_failing_execution_results, get_and_write_diff

pytestmark = [
    pytest.mark.anyio,
]


async def test_catalog_are_the_same(
    record_property: Callable,
    request: SubRequest,
    discover_control_execution_result: ExecutionResult,
    discover_target_execution_result: ExecutionResult,
) -> None:
    """This test runs the discover command on both the control and target connectors.
    It makes sure that the discover command returns the same catalog for both connectors.
    A catalog diff is generated and stored in the test artifacts if the catalogs are not the same.
    """
    fail_test_on_failing_execution_results(
        record_property,
        [
            discover_control_execution_result,
            discover_target_execution_result,
        ],
    )

    def get_catalog(execution_result: ExecutionResult) -> AirbyteCatalog:
        for message in execution_result.airbyte_messages:
            if message.type is Type.CATALOG and message.catalog:
                return message.catalog
        return None

    control_catalog = get_catalog(discover_control_execution_result)
    target_catalog = get_catalog(discover_target_execution_result)

    if control_catalog is None:
        pytest.skip("The control discover did not return a catalog, we cannot compare the results.")

    if target_catalog is None:
        pytest.fail("The target discover did not return a catalog. Check the test artifacts for more information.")

    control_streams = {c.name: c for c in control_catalog.streams}
    target_streams = {t.name: t for t in target_catalog.streams}

    catalog_diff_path_prefix = "catalog_diff"
    catalog_diff = get_and_write_diff(
        request,
        _get_filtered_sorted_streams(control_streams, target_streams.keys(), True),
        _get_filtered_sorted_streams(target_streams, control_streams.keys(), True),
        catalog_diff_path_prefix,
        True,
        None,
    )

    control_streams_diff_path_prefix = "control_streams_diff"
    control_streams_diff = get_and_write_diff(
        request,
        _get_filtered_sorted_streams(control_streams, target_streams.keys(), False),
        [],
        control_streams_diff_path_prefix,
        True,
        None,
    )

    target_streams_diff_path_prefix = "target_streams_diff"
    target_streams_diff = get_and_write_diff(
        request,
        [],
        _get_filtered_sorted_streams(target_streams, control_streams.keys(), False),
        target_streams_diff_path_prefix,
        True,
        None,
    )

    has_diff = catalog_diff or control_streams_diff or target_streams_diff

    if has_diff:
        record_property("Catalog diff", catalog_diff)
        record_property("Control streams diff", control_streams_diff)
        record_property("Target streams diff", target_streams_diff)

        if control_streams.keys() != target_streams.keys():
            pytest.fail(
                f"The set of streams in the control and target catalogs do not match. control_streams={', '.join(control_streams.keys())} target_streams={', '.join(target_streams.keys())}. Detailed diff is stored in Diff is stored at {catalog_diff}, {control_streams_diff}, and {target_streams_diff}."
            )

        else:
            pytest.fail(
                f"The control and target output are not the same. Diff is stored at {catalog_diff}, {control_streams_diff}, and {target_streams_diff}."
            )


def _get_filtered_sorted_streams(streams: dict[str, AirbyteStream], stream_set: Iterable[str], include_target: bool) -> list[dict]:
    return sorted(
        filter(
            lambda x: (x["name"] in stream_set if include_target else x["name"] not in stream_set),
            [json.loads(s.json(sort_keys=True)) for s in streams.values()],
        ),
        key=lambda x: x["name"],
    )
