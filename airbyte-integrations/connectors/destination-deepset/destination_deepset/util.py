# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from time import time
from traceback import format_exc
from typing import Any
from urllib.parse import unquote, urlparse

from pydantic import BaseModel

from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    DestinationSyncMode,
    FailureType,
    Level,
    TraceType,
    Type,
)


def get(obj: dict[str, Any] | BaseModel, key_path: str, default: Any = None) -> Any:
    """Get the value of an arbitrarily nested key in a dictionary or Pydantic model instance

    Args:
        obj (Any): The object from which the value is to be extracted.
        key_path (str): A dotted path to the key to be extracted.
        default (Any, optional): The fallback value if the given key does not exist. Defaults to None.

    Returns:
        Any: The value found at the specified key path.
    """
    obj = obj if isinstance(obj, dict) else obj.model_dump()

    current = obj
    keys = key_path.split(".")

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def get_trace_message(message: str, exception: Exception | None = None) -> AirbyteMessage:
    """Return a the message formatted as an `AirbyteMessage` of type `TRACE`.

    Args:
        message (str): The message to be formatted.
        exception (Exception | None, optional): An optional `Exception` object. Defaults to None.

    Returns:
        AirbyteMessage: An `AirbyteMessage` instance.
    """
    return AirbyteMessage(
        type=Type.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=time(),
            error=AirbyteErrorTraceMessage(
                message=message,
                internal_message=str(exception) if exception else None,
                stack_trace=format_exc(),
                failure_type=FailureType.transient_error.value,
            ),
        ),
    )


def get_log_message(message: str) -> AirbyteMessage:
    """Return the message formatted as an `AirbyteMessage` of type `LOG`.

    Args:
        message (str): The message to be formatted.

    Returns:
        AirbyteMessage: An `AirbyteMessage` instance.
    """
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message))


def get_file_write_mode(destination_sync_mode: DestinationSyncMode) -> str:
    """Translates Airbytes `DestinationSyncMode` into deepset Clouds's `WriteMode`.

    Args:
        destination_sync_mode (DestinationSyncMode): The destination sync mode.

    Returns:
        str: The equivalent write mode.
    """
    fallback_keep = "KEEP"
    write_modes = {
        DestinationSyncMode.append: "FAIL",
        DestinationSyncMode.append_dedup: fallback_keep,
        DestinationSyncMode.overwrite: "OVERWRITE",
    }
    return write_modes.get(destination_sync_mode) or fallback_keep


def generate_name(document_key: str, stream: str, namespace: str | None = None) -> str:
    """Generate a unique name for the record using the document key.

    Args:
        document_key (str): The document key for the record.
        stream (str): The name of the stream that the record belongs to.
        namespace (str | None, optional): The namespace of the record. Defaults to None.

    Returns:
        str: The unique name of the record.
    """
    prefix = [p for p in [stream, namespace] if p]
    # Parse URL and get path segments
    parsed = urlparse(document_key)
    path_segments = [*prefix, *parsed.path.strip("/").split("/")]

    # Join segments with underscores to create filename
    filename = "_".join(path_segments)

    # URL decode the filename to handle special characters
    return unquote(filename).replace(" ", "-")
