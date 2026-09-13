"""The high-water mark has to order values exactly, not approximately.

`float(value)` was chosen to stop "9" beating "10" lexicographically, and it
does -- but it also rounds. SAP's NUMC and DEC columns are decimal strings that
can be longer than a double's 53 bits of mantissa, and two adjacent values then
produce the same key: the cursor never advances past the boundary and the sync
re-reads the same rows every run, forever, with nothing in the logs.
"""

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository

from source_sap.cursors import FieldValueCursor


def _cursor(initial):
    return FieldValueCursor(
        "S", None, InMemoryMessageRepository(), ConnectorStateManager(), "C", {"C": initial} if initial else {}
    )


def _record(value):
    record = MagicMock()
    record.data = {"C": value}
    return record


class TestLargeIntegerCursors:
    @pytest.mark.parametrize(
        ("lower", "higher"),
        [
            ("9007199254740992", "9007199254740993"),  # 2**53 and its successor
            ("123456789012345678", "123456789012345679"),
            ("99999999999999999999", "100000000000000000000"),
        ],
    )
    def test_the_cursor_advances_past_the_double_boundary(self, lower, higher):
        cursor = _cursor(lower)
        cursor.observe(_record(higher))
        assert cursor.state["C"] == higher, "the cursor stalled; the next run re-reads this row"

    def test_it_does_not_go_backwards(self):
        cursor = _cursor("9007199254740993")
        cursor.observe(_record("9007199254740992"))
        assert cursor.state["C"] == "9007199254740993"


class TestDecimalCursors:
    def test_a_long_decimal_advances(self):
        cursor = _cursor("1.00000000000000000001")
        cursor.observe(_record("1.00000000000000000002"))
        assert cursor.state["C"] == "1.00000000000000000002"


class TestTheOrdinaryCases:
    def test_ten_still_beats_nine(self):
        # The reason the numeric branch exists at all.
        cursor = _cursor("9")
        cursor.observe(_record("10"))
        assert cursor.state["C"] == "10"

    def test_dats_values_still_order(self):
        cursor = _cursor("20260101")
        cursor.observe(_record("20260202"))
        assert cursor.state["C"] == "20260202"

    def test_iso_timestamps_still_order(self):
        cursor = _cursor("2026-01-01T00:00:00")
        cursor.observe(_record("2026-02-02T00:00:00"))
        assert cursor.state["C"] == "2026-02-02T00:00:00"

    def test_a_numeric_still_sorts_before_a_non_numeric(self):
        cursor = _cursor("5")
        cursor.observe(_record("ABC"))
        assert cursor.state["C"] == "ABC"


class TestValuesThatOnlyLookNumeric:
    @pytest.mark.parametrize("odd", ["NaN", "Infinity", "-Infinity"])
    def test_they_are_treated_as_text(self, odd):
        # Decimal parses all three; none of them is a position in a stream.
        cursor = _cursor("100")
        cursor.observe(_record(odd))
        assert cursor.state["C"] == odd, "a non-finite value must sort as text, not as a number"

    def test_and_a_real_number_still_beats_text(self):
        cursor = _cursor("NaN")
        cursor.observe(_record("100"))
        assert cursor.state["C"] == "NaN"
