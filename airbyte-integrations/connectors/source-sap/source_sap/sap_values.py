"""Parsing SAP's scalar wire formats.

SAP writes a date as ``20260102`` and a time as ``103000``; a connector config is
JSON, so values arrive as strings in either the SAP form or the ISO one. These
accept both and emit ISO, which is what DuckDB and JSON Schema want.

Separate from any one protocol: these are facts about SAP, not about calling
function modules.
"""

from __future__ import annotations

import datetime
from typing import Any

#: Longest value the connector will carry from Airbyte state into a SAP
#: statement. State is replayed by the platform, so it is not always ours; SAP
#: takes a WHERE fragment as 72-character lines and a BICS variable or RFC
#: parameter is narrower still, so a multi-kilobyte value dumps or truncates
#: inside SAP rather than failing here. Real checkpoints are short -- a DATS
#: value is 8 characters.
MAX_STATE_VALUE = 255


def checked_state_value(field: str, value: Any) -> str:
    """A state value on its way into a SAP statement, or a message naming it."""
    text = str(value)
    if len(text) > MAX_STATE_VALUE:
        raise ValueError(
            f"The state value for {field} is {len(text)} characters, over the "
            f"{MAX_STATE_VALUE} this connector will send to SAP. Reset the stream's state."
        )
    return text


#: Keyed by length wherever SAP's form is digits only. `strptime` is greedy --
#: it reads "2026012" as %Y%m%d quite happily, and "1030" as %H%M%S -- so a
#: config typo would become a valid but different value, and the wrong selection
#: would reach SAP with the sync still green.
_DATE_BY_LENGTH = {8: "%Y%m%d"}
_DATE_FORMATS = ("%Y-%m-%d",)
_TIME_BY_LENGTH = {6: "%H%M%S", 4: "%H%M"}
_TIME_FORMATS = ("%H:%M:%S", "%H:%M")
_TIMESTAMP_BY_LENGTH = {14: "%Y%m%d%H%M%S"}
_TIMESTAMP_FORMATS = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S")


def _parse(
    value: str,
    formats: tuple[str, ...],
    what: str,
    shape: str,
    by_length: dict[int, str] | None = None,
) -> datetime.datetime:
    text = str(value).strip()
    if by_length is not None and text.isdigit():
        fmt = by_length.get(len(text))
        if fmt is None:
            raise ValueError(f"{value!r} is not a {what} (expected {shape})")
        formats = (fmt,)
    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(f"{value!r} is not a {what} (expected {shape})")


def sap_date(value: str) -> str:
    """SAP DATS or ISO in, ISO date out."""
    return _parse(value, _DATE_FORMATS, "date", "YYYYMMDD or YYYY-MM-DD", _DATE_BY_LENGTH).date().isoformat()


def sap_time(value: str) -> str:
    """SAP TIMS or ISO in, ISO time out."""
    return _parse(value, _TIME_FORMATS, "time", "HHMMSS or HH:MM:SS", _TIME_BY_LENGTH).time().isoformat()


def sap_timestamp(value: str) -> str:
    """SAP UTC long form or ISO in, ISO timestamp out."""
    return _parse(
        value,
        _TIMESTAMP_FORMATS,
        "timestamp",
        "YYYYMMDDHHMMSS or an ISO timestamp",
        _TIMESTAMP_BY_LENGTH,
    ).isoformat(sep=" ")
