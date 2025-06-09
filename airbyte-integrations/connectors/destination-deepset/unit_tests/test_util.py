# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any

import pytest
from destination_deepset import util
from pydantic import BaseModel

from airbyte_cdk.models import AirbyteMessage, DestinationSyncMode, FailureType, Level, TraceType, Type


class Simple(BaseModel):
    name: str


class Nested(BaseModel):
    simple: Simple
    adjacent: bool


@pytest.mark.parametrize(
    ("obj", "key_path", "expected"),
    [
        ({}, "a.b", None),  # default fallback value is None
        ({"a": {"b": 5}}, "a.b", 5),
        ({"a": {"b": 5}}, "a.b.c", None),  # fallback
        # Should work for Pydantic models too
        (Simple(name="Jack"), "name", "Jack"),
        (Simple(name="Jack"), "name.last", None),  # fallback
        (Nested(simple=Simple(name="Jack"), adjacent=False), "adjacent", False),
        (Nested(simple=Simple(name="Jack"), adjacent=False), "simple.name", "Jack"),
    ],
)
def test_get(obj: Any, key_path: str, expected: Any) -> None:
    assert util.get(obj=obj, key_path=key_path) == expected


def test_get_ignores_fallback_value_if_match_found() -> None:
    fallback = "I Fall Back"
    obj = {"a": {"b": {"c": "I Don't Fall Back"}}}
    assert util.get(obj=obj, key_path="a.b.c", default=fallback) != fallback
    assert util.get(obj=obj, key_path="a.b.c", default=fallback) == "I Don't Fall Back"


def test_get_returns_fallback_value_if_no_match_found() -> None:
    fallback = "I Fall Back"
    assert util.get(obj={}, key_path="a.b.c", default=fallback) == fallback


@pytest.mark.parametrize(
    ("message", "exception", "expected"),
    [
        ("Hello", None, ("Hello", None)),
        ("Hello", Exception("World"), ("Hello", "World")),
    ],
)
def test_get_trace_message(message: str, exception: Exception | None, expected: tuple[str, str | None]) -> None:
    error_message, internal_error_message = expected
    airbyte_message = util.get_trace_message(message, exception=exception)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == Type.TRACE
    assert airbyte_message.trace.type == TraceType.ERROR
    assert airbyte_message.trace.error.message == error_message
    assert airbyte_message.trace.error.internal_message == internal_error_message
    assert airbyte_message.trace.error.failure_type == FailureType.transient_error.value


def test_get_log_message() -> None:
    log_message = "Hello, World!"
    airbyte_message = util.get_log_message(log_message)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == Type.LOG
    assert airbyte_message.log.level == Level.INFO
    assert airbyte_message.log.message == log_message
    assert airbyte_message.log.stack_trace is None


@pytest.mark.parametrize(
    ("destination_sync_mode", "write_mode"),
    [
        (DestinationSyncMode.append, "FAIL"),
        (DestinationSyncMode.append_dedup, "KEEP"),
        (DestinationSyncMode.overwrite, "OVERWRITE"),
    ],
)
def test_get_file_write_mode(destination_sync_mode: DestinationSyncMode, write_mode: str) -> None:
    assert util.get_file_write_mode(destination_sync_mode) == write_mode


@pytest.mark.parametrize(
    ("document_key", "stream", "namespace", "expected"),
    [
        ("testdoc_pdf.pdf", "unstructured", None, "unstructured_testdoc_pdf.pdf"),
        ("testdoc_pdf.pdf", "unstructured", "docs", "unstructured_docs_testdoc_pdf.pdf"),
        (
            "https://airbyte179.sharepoint.com/Shared%20Documents/Test_folder/Test_foler_2_1/simple_pdf_file.pdf",
            "unstructured",
            "docs",
            "unstructured_docs_Shared-Documents_Test_folder_Test_foler_2_1_simple_pdf_file.pdf",
        ),
        (
            "https://airbyte179.sharepoint.com/Shared%20Documents/Test_folder/Test_foler_2_1/simple_pdf_file.pdf",
            "unstructured",
            "",
            "unstructured_Shared-Documents_Test_folder_Test_foler_2_1_simple_pdf_file.pdf",
        ),
    ],
)
def test_generate_name(document_key: str, stream: str | None, namespace: str | None, expected: str) -> None:
    assert util.generate_name(document_key, stream, namespace) == expected
