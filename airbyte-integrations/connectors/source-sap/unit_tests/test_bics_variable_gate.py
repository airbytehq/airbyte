"""What the mandatory-variable gate promises, and what it does when it cannot see.

docs/bw-queries.md says the connector "refuses the configuration" when a
mandatory, input-ready BEx variable has no value. Two holes: introspection
failure was swallowed silently, so the promise quietly did not apply; and a
`variant` fills variables server-side, which the gate did not count as bound.
"""

import logging
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from source_sap.protocols.bics import BicsDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def _driver(**obj):
    return BicsDriver(
        {**CONN, "protocol": {"mode": "bics", "objects": [{"name": "Q", "cube": "C", "query": "QRY", **obj}]}}
    )


def _cursor(rows=None, raises=None):
    cursor = MagicMock()
    if raises is not None:
        cursor.execute.side_effect = raises
    else:
        cursor.execute.return_value.fetchall.return_value = rows or []
    return cursor


MANDATORY = [("0CALMONTH", True, True)]


class TestAnUnboundMandatoryVariable:
    def test_is_refused(self):
        driver = _driver()
        with pytest.raises(AirbyteTracedException) as caught:
            driver._assert_mandatory_variables_bound(_cursor(MANDATORY), driver._object_overrides()["Q"], "C")
        assert "0CALMONTH" in str(caught.value)

    def test_a_bound_one_is_accepted(self):
        driver = _driver(variables=[{"name": "0CALMONTH", "low": "202601"}])
        driver._assert_mandatory_variables_bound(_cursor(MANDATORY), driver._object_overrides()["Q"], "C")

    def test_a_variant_counts_as_binding_them(self):
        # The variant fills the query's variables on the BW side; the connector
        # cannot see which, so it cannot claim any is missing.
        driver = _driver(variant="MY_VARIANT")
        driver._assert_mandatory_variables_bound(_cursor(MANDATORY), driver._object_overrides()["Q"], "C")


class TestWhenIntrospectionFails:
    def test_the_configuration_is_not_refused(self):
        # Failing closed here would break queries whose variables BW will not
        # enumerate, which is a working configuration today.
        driver = _driver()
        driver._assert_mandatory_variables_bound(
            _cursor(raises=RuntimeError("BICS_PROV_VAR_GET_VARIABLES not authorized")),
            driver._object_overrides()["Q"],
            "C",
        )

    def test_but_it_says_the_check_did_not_run(self, caplog):
        driver = _driver()
        with caplog.at_level(logging.WARNING):
            driver._assert_mandatory_variables_bound(
                _cursor(raises=RuntimeError("not authorized")), driver._object_overrides()["Q"], "C"
            )
        assert "QRY" in caplog.text and "not authorized" in caplog.text
