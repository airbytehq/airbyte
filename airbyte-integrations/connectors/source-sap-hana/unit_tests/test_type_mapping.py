import datetime as dt
from decimal import Decimal

import pytest

from source_sap_hana.type_mapping import ValueConverter, cursor_param_parser, json_schema_for


@pytest.mark.parametrize(
    "hana_type, expected",
    [
        ("INTEGER", {"type": ["null", "integer"]}),
        ("BIGINT", {"type": ["null", "integer"]}),
        ("DECIMAL", {"type": ["null", "number"]}),
        ("DOUBLE", {"type": ["null", "number"]}),
        ("NVARCHAR", {"type": ["null", "string"]}),
        ("BOOLEAN", {"type": ["null", "boolean"]}),
        ("DATE", {"type": ["null", "string"], "format": "date"}),
        ("VARBINARY", {"type": ["null", "string"], "contentEncoding": "base64"}),
        ("SOMETHING_NEW", {"type": ["null", "string"]}),
    ],
)
def test_json_schema_for(hana_type, expected):
    assert json_schema_for(hana_type) == expected


def test_timestamp_schema_is_without_timezone():
    schema = json_schema_for("TIMESTAMP")
    assert schema["format"] == "date-time"
    assert schema["airbyte_type"] == "timestamp_without_timezone"


def test_decimal_as_string_schema():
    assert json_schema_for("DECIMAL", decimal_as_string=True) == {"type": ["null", "string"]}


def test_value_converter():
    c = ValueConverter()
    assert c(None) is None
    assert c(Decimal("12.50")) == 12.5
    assert c(Decimal("100.00")) == 100
    assert isinstance(c(Decimal("100.00")), int)
    assert c(dt.date(2026, 1, 31)) == "2026-01-31"
    assert c(dt.datetime(2026, 1, 31, 10, 5, 3, 120000)) == "2026-01-31T10:05:03.120000"
    assert c(dt.time(23, 59)) == "23:59:00"
    assert c(b"\x00\x01") == "AAE="
    assert c("MAT\x00ERIALE") == "MATERIALE"


def test_value_converter_keeps_nul_when_disabled():
    assert ValueConverter(strip_nul_characters=False)("A\x00B") == "A\x00B"


def test_decimal_as_string_preserves_precision():
    assert ValueConverter(decimal_as_string=True)(Decimal("12345678901234567890.12")) == "12345678901234567890.12"


def test_lob_is_read():
    class FakeLob:
        def read(self):
            return "long text\x00"

    assert ValueConverter()(FakeLob()) == "long text"


def test_cursor_param_parser_roundtrip():
    c = ValueConverter()
    ts = dt.datetime(2026, 9, 1, 8, 30, 0, 123456)
    assert cursor_param_parser("TIMESTAMP")(c(ts)) == ts
    assert cursor_param_parser("DATE")(c(dt.date(2026, 9, 1))) == dt.date(2026, 9, 1)
    assert cursor_param_parser("DECIMAL")(c(Decimal("10.25"))) == Decimal("10.25")
    assert cursor_param_parser("NVARCHAR")("20260901") == "20260901"
