"""Every path from Airbyte state into a SAP statement, not just the first one.

Round 4 bounded the RFC cursor value on the grounds that state is not always
ours -- a resumed connection replays whatever blob the platform stored. The BICS
watermark and the rfc_invoke cursor parameter are the same kind of path and were
left unbounded, so a 100 KB state value became a 100 KB literal inside a BICS
variable or an RFC parameter: SAP dumps or truncates, and neither is a message
anyone can act on.

Parameterised over the drivers deliberately: a fourth sink added later should
fail this file rather than be discovered by a fifth review round.
"""

import pytest

from source_sap.protocols.base import SapObject
from source_sap.protocols.bics import BicsDriver
from source_sap.protocols.rfc import RfcDriver
from source_sap.protocols.rfc_invoke import RfcInvokeDriver
from source_sap.sap_values import MAX_STATE_VALUE

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}
TOO_LONG = "A" * (MAX_STATE_VALUE + 1)
LONGEST_ALLOWED = "A" * MAX_STATE_VALUE


def _rfc(value):
    driver = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", "cursor_field": "ERDAT"}]}})
    obj = SapObject(
        name="T",
        json_schema={},
        supports_incremental=True,
        meta={"table": "T", "cursor_field": "ERDAT", "cursor_sap_type": "CHAR"},
    )
    return driver.read_plans(None, obj, incremental=True, state={"ERDAT": value})


def _bics(value):
    driver = BicsDriver(
        {
            **CONN,
            "protocol": {
                "mode": "bics",
                "objects": [{"name": "Q", "cube": "C", "query": "Q", "cursor_variable": "V", "cursor_field": "F"}],
            },
        }
    )
    obj = SapObject(name="Q", json_schema={}, meta={"cube": "C", "query": "Q", "session_id": "s"})
    return driver.read_plans(None, obj, incremental=True, state={"F": value})


def _rfc_invoke(value):
    driver = RfcInvokeDriver(
        {
            **CONN,
            "protocol": {
                "mode": "rfc_invoke",
                "objects": [
                    {"name": "F", "function": "BAPI_X", "cursor_field": "FLDATE", "cursor_parameter": "DATE_FROM"}
                ],
            },
        }
    )
    obj = SapObject(
        name="F",
        json_schema={},
        supports_incremental=True,
        meta={"function": "BAPI_X", "cursor_field": "FLDATE", "cursor_parameter": "DATE_FROM"},
    )
    return driver.read_plans(None, obj, incremental=True, state={"FLDATE": value})


SINKS = {"rfc": _rfc, "bics": _bics, "rfc_invoke": _rfc_invoke}


@pytest.mark.parametrize("sink", sorted(SINKS))
class TestEveryStateSink:
    def test_rejects_an_over_long_value(self, sink):
        with pytest.raises(ValueError):
            SINKS[sink](TOO_LONG)

    def test_says_which_field_it_was(self, sink):
        with pytest.raises(ValueError) as caught:
            SINKS[sink](TOO_LONG)
        message = str(caught.value)
        assert any(name in message for name in ("ERDAT", "F", "FLDATE")), message

    def test_accepts_a_value_at_the_bound(self, sink):
        assert SINKS[sink](LONGEST_ALLOWED)

    def test_the_over_long_value_never_reaches_the_sql(self, sink):
        try:
            plans = SINKS[sink](TOO_LONG)
        except ValueError:
            return
        for plan in plans:
            assert TOO_LONG not in plan.sql
            assert TOO_LONG not in " ".join(str(v) for v in (plan.meta.get("setup") or []))
