"""A cursor value comes back from state, and state is not always ours.

Quoting is handled -- `_sql_literal` doubles quotes at both levels -- but length
is not: SAP's RFC_READ_TABLE takes its WHERE fragment as 72-character lines, and
a value of a few kilobytes produces a dump or a truncation rather than our own
error message. A checkpointed DATS value is 8 characters; anything approaching
this bound is a corrupted or forged state blob.
"""

import pytest

from source_sap.protocols.base import SapObject
from source_sap.protocols.rfc import MAX_CURSOR_VALUE, RfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def _plans(value, sap_type="DATS"):
    driver = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", "cursor_field": "ERDAT"}]}})
    target = SapObject(
        name="T",
        json_schema={},
        supports_incremental=True,
        meta={"table": "T", "cursor_field": "ERDAT", "cursor_sap_type": sap_type},
    )
    return driver.read_plans(None, target, incremental=True, state={"ERDAT": value})


class TestAnOverLongCursorValueIsRejected:
    def test_a_normal_value_is_used(self):
        assert "20260905" in _plans("2026-09-05")[0].sql

    def test_a_value_past_the_bound_raises_our_error(self):
        with pytest.raises(ValueError) as caught:
            _plans("A" * (MAX_CURSOR_VALUE + 1), sap_type="CHAR")
        assert "ERDAT" in str(caught.value)

    def test_the_bound_itself_is_allowed(self):
        assert _plans("A" * MAX_CURSOR_VALUE, sap_type="CHAR")


class TestAMalformedCursorValueIsRejected:
    """Truncating a malformed value is the same defect as parsing it greedily.

    `sap_cursor_literal` sliced: a DATS state of "20260905120000" became
    "20260905" and a TIMS state of "10300000" became "103000" -- a different
    selection than the state recorded, sent to SAP with the sync green. Round 4
    fixed exactly this in `sap_values`; this is the path that still sliced.
    """

    @pytest.mark.parametrize("given", ["20260905120000", "2026090", "202609051"])
    def test_a_date_that_is_not_a_date_is_rejected(self, given):
        with pytest.raises(ValueError) as caught:
            _plans(given)
        assert "ERDAT" in str(caught.value)

    @pytest.mark.parametrize(
        ("given", "expected"),
        [("2026-09-05", "20260905"), ("2026-9-5", "20260905"), ("20260905", "20260905")],
    )
    def test_a_real_date_still_reaches_sap_in_ddic_form(self, given, expected):
        assert f"ERDAT >= ''{expected}''" in _plans(given)[0].sql

    @pytest.mark.parametrize("given", ["10300000", "1030000"])
    def test_a_time_that_is_not_a_time_is_rejected(self, given):
        with pytest.raises(ValueError):
            _plans(given, sap_type="TIMS")

    @pytest.mark.parametrize(("given", "expected"), [("10:30:00", "103000"), ("10:3:0", "100300")])
    def test_a_real_time_still_reaches_sap_in_ddic_form(self, given, expected):
        assert f"ERDAT >= ''{expected}''" in _plans(given, sap_type="TIMS")[0].sql

    def test_a_timestamp_keeps_its_fourteen_digits(self):
        assert "ERDAT >= ''20260905103000''" in _plans("2026-09-05 10:30:00", sap_type="UTCLONG")[0].sql

    @pytest.mark.parametrize("given", ["2026-09-05", "20260905103"])
    def test_a_timestamp_that_is_not_one_is_rejected(self, given):
        with pytest.raises(ValueError):
            _plans(given, sap_type="UTCLONG")

    def test_an_untyped_cursor_is_passed_through(self):
        # No DDIC type means no form to check against; quoting still applies.
        assert "ERDAT >= ''ABC''" in _plans("ABC", sap_type=None)[0].sql
