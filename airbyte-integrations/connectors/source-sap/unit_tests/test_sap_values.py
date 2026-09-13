"""SAP scalar value parsing, extracted from the invoke driver.

These are about SAP's wire formats, not about calling function modules, and two
protocols now need them.
"""

import pytest

from source_sap.sap_values import sap_date, sap_time, sap_timestamp


class TestSapDate:
    @pytest.mark.parametrize(
        "given,expected",
        [
            ("20260102", "2026-01-02"),
            ("2026-01-02", "2026-01-02"),
            (" 20260102 ", "2026-01-02"),
        ],
    )
    def test_accepted_forms(self, given, expected):
        assert sap_date(given) == expected

    @pytest.mark.parametrize("bad", ["not-a-date", "20261301", "", "2026"])
    def test_rejected_forms(self, bad):
        with pytest.raises(ValueError):
            sap_date(bad)


class TestSapTime:
    @pytest.mark.parametrize(
        "given,expected",
        [
            ("103000", "10:30:00"),
            ("10:30:00", "10:30:00"),
            ("1030", "10:30:00"),
            ("10:30", "10:30:00"),
        ],
    )
    def test_accepted_forms(self, given, expected):
        assert sap_time(given) == expected

    @pytest.mark.parametrize("bad", ["251000", "nonsense", ""])
    def test_rejected_forms(self, bad):
        with pytest.raises(ValueError):
            sap_time(bad)


class TestSapTimestamp:
    @pytest.mark.parametrize(
        "given",
        [
            "20260102103000",
            "2026-01-02T10:30:00",
            "2026-01-02 10:30:00",
        ],
    )
    def test_accepted_forms(self, given):
        assert sap_timestamp(given) == "2026-01-02 10:30:00"

    def test_rejected_form(self):
        with pytest.raises(ValueError):
            sap_timestamp("yesterday")


class TestDigitOnlyInputIsFixedWidth:
    """SAP's compact forms are fixed-width, and `strptime` is not.

    `strptime('2026012', '%Y%m%d')` happily yields 2026-01-02, so a config typo
    with a digit missing becomes a valid but *different* date: the filter that
    reaches SAP selects the wrong rows and the sync stays green. The same shape
    made `sap_time('1030')` return 10:03:00.
    """

    @pytest.mark.parametrize("typo", ["2026012", "202601021", "2026102"])
    def test_a_date_of_the_wrong_length_is_rejected(self, typo):
        with pytest.raises(ValueError):
            sap_date(typo)

    def test_a_correct_date_still_parses(self):
        assert sap_date("20260102") == "2026-01-02"

    @pytest.mark.parametrize("typo", ["202601021030", "2026010210300", "2026010210"])
    def test_a_timestamp_of_the_wrong_length_is_rejected(self, typo):
        with pytest.raises(ValueError):
            sap_timestamp(typo)

    def test_a_correct_timestamp_still_parses(self):
        assert sap_timestamp("20260102103000") == "2026-01-02 10:30:00"

    @pytest.mark.parametrize("typo", ["10300", "1030000", "103"])
    def test_a_time_of_the_wrong_length_is_rejected(self, typo):
        with pytest.raises(ValueError):
            sap_time(typo)

    def test_iso_forms_are_unaffected_by_the_length_rule(self):
        assert sap_date("2026-01-02") == "2026-01-02"
        assert sap_time("10:30:00") == "10:30:00"
        assert sap_timestamp("2026-01-02T10:30:00") == "2026-01-02 10:30:00"
