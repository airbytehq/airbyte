"""Mapping SAP/ERPL failures onto Airbyte's failure taxonomy."""

from __future__ import annotations

import re

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

# SAP-side conditions the user can fix by changing configuration or SAP authorizations.
_CONFIG_PATTERNS = (
    r"RFC_LOGON_FAILURE",
    r"Name or password is incorrect",
    r"authoriz",
    r"NO_AUTHORITY",
    r"not authorized",
    r"unknown host",
    r"Cannot resolve",
    r"connection refused",
    r"does not exist",
    r"not found",
    r"TABLE_NOT_AVAILABLE",
    r"INVALID_CLIENT",
    r"Could not open the ICU common library",
)
# Conditions that usually clear on their own; the platform may retry these.
_TRANSIENT_PATTERNS = (
    r"SYSTEM_FAILURE",
    r"shortdump",
    r"RESOURCE_FAILURE",
    r"no free work process",
    r"COMMUNICATION_FAILURE",
    r"time.?out",
    r"connection reset",
    r"LOCK",
    r"ENQUEUE",
    r"TSV_TNEW_PAGE_ALLOC_FAILED",
    r"MEMORY_NO_MORE",
)


def classify(message: str) -> FailureType:
    """Best-effort classification of an ERPL/SAP error string."""
    for pattern in _CONFIG_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return FailureType.config_error
    for pattern in _TRANSIENT_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return FailureType.transient_error
    return FailureType.system_error


def config_error(message: str, exception: BaseException | None = None) -> AirbyteTracedException:
    return AirbyteTracedException(
        message=message,
        internal_message=str(exception) if exception else message,
        failure_type=FailureType.config_error,
        exception=exception,
    )


def traced(message: str, exception: BaseException, stream_name: str | None = None) -> AirbyteTracedException:
    """Wrap an ERPL exception, inferring the failure type from its text."""
    from airbyte_cdk.models import StreamDescriptor

    detail = str(exception)
    return AirbyteTracedException(
        message=f"{message}: {detail.splitlines()[0] if detail else exception!r}",
        internal_message=detail,
        failure_type=classify(detail),
        exception=exception,
        stream_descriptor=StreamDescriptor(name=stream_name) if stream_name else None,
    )
