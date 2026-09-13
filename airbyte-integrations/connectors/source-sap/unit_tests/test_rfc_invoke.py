"""Calling arbitrary RFC function modules as streams.

Two properties matter more than anything else here:

* `discover` must never invoke a function module. Probing `BAPI_*_CREATE` to
  learn its shape would be unacceptable in a source connector, so the schema is
  derived from `sap_rfc_describe_function` metadata alone.
* A BAPI reports failure in a `RETURN` table rather than by raising, so an
  unchecked call turns a failure into an empty stream.
"""

from unittest.mock import MagicMock

import pytest

from source_sap.protocols.base import ReadPlan, SapObject, sql_struct_literal
from source_sap.protocols.rfc_invoke import RfcInvokeDriver, is_bapi_failure

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}
FLIGHT_STRUCT = "STRUCT(AIRLINEID VARCHAR, CONNECTID VARCHAR, FLIGHTDATE DATE, PRICE DECIMAL(23,4))[]"


def driver(*objects, **protocol):
    return RfcInvokeDriver({**CONN, "protocol": {"mode": "rfc_invoke", "objects": list(objects), **protocol}})


def _obj(**meta):
    base = {"function": "BAPI_FLIGHT_GETLIST", "path": "/FLIGHT_LIST", "parameters": {}}
    base.update(meta)
    return SapObject(name=base.get("name", "flights"), json_schema={}, meta=base)


class TestStructLiteral:
    def test_a_flat_mapping_becomes_a_duckdb_struct(self):
        assert sql_struct_literal({"AIRLINE": "LH"}) == "{'AIRLINE': 'LH'}"

    def test_numbers_and_booleans_keep_their_type(self):
        got = sql_struct_literal({"MAX_ROWS": 100, "FLAG": True})
        assert "'MAX_ROWS': 100" in got and "'FLAG': true" in got

    def test_null_is_rendered_as_null(self):
        assert sql_struct_literal({"X": None}) == "{'X': NULL}"

    def test_nested_structures_recurse(self):
        got = sql_struct_literal({"DESTINATION_FROM": {"AIRPORTID": "FRA"}})
        assert got == "{'DESTINATION_FROM': {'AIRPORTID': 'FRA'}}"

    def test_lists_become_duckdb_lists(self):
        got = sql_struct_literal({"DATE_RANGE": [{"SIGN": "I", "LOW": "20260101"}]})
        assert got == "{'DATE_RANGE': [{'SIGN': 'I', 'LOW': '20260101'}]}"

    @pytest.mark.parametrize("hostile", ["x'); DROP TABLE y; --", "a' OR '1'='1", "it's"])
    def test_hostile_values_stay_inside_their_literal(self, hostile):
        got = sql_struct_literal({"K": hostile, "N": [hostile]})
        assert got.count("'") % 2 == 0

    def test_hostile_keys_are_escaped_too(self):
        got = sql_struct_literal({"k'): x": "v"})
        assert got.count("'") % 2 == 0


class TestSchemaWithoutInvoking:
    def test_a_table_path_expands_to_its_fields(self, tmp_path):
        import duckdb

        con = duckdb.connect()
        schema = RfcInvokeDriver.schema_for_duckdb_type(con, FLIGHT_STRUCT)
        con.close()
        assert set(schema["properties"]) == {"AIRLINEID", "CONNECTID", "FLIGHTDATE", "PRICE"}
        assert schema["properties"]["FLIGHTDATE"]["format"] == "date"
        assert schema["properties"]["PRICE"]["type"] == ["null", "number"]

    def test_a_scalar_struct_expands_too(self):
        import duckdb

        con = duckdb.connect()
        schema = RfcInvokeDriver.schema_for_duckdb_type(con, "STRUCT(ECHOTEXT VARCHAR, RESPTEXT VARCHAR)")
        con.close()
        assert set(schema["properties"]) == {"ECHOTEXT", "RESPTEXT"}

    def test_an_unparseable_type_is_a_config_error(self):
        import duckdb
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        con = duckdb.connect()
        with pytest.raises(AirbyteTracedException, match="NOT A TYPE"):
            RfcInvokeDriver.schema_for_duckdb_type(con, "NOT A TYPE(((")
        con.close()


class TestParameterValidation:
    DESCRIBE = {
        "import": [{"name": "AIRLINE", "duckdb_type": "VARCHAR"}, {"name": "MAX_ROWS", "duckdb_type": "BIGINT"}],
        "export": [],
        "changing": [],
        "tables": [
            {"name": "FLIGHT_LIST", "duckdb_type": FLIGHT_STRUCT},
            {"name": "RETURN", "duckdb_type": 'STRUCT("TYPE" VARCHAR)[]'},
        ],
    }

    def test_a_known_parameter_is_accepted(self):
        driver().validate_parameters("BAPI_X", {"AIRLINE": "LH"}, self.DESCRIBE)

    def test_an_unknown_parameter_is_refused(self):
        # A typo would otherwise surface as an opaque SAP dump.
        with pytest.raises(Exception, match="AIRLIN"):
            driver().validate_parameters("BAPI_X", {"AIRLIN": "LH"}, self.DESCRIBE)

    def test_the_error_lists_what_is_available(self):
        with pytest.raises(Exception, match="MAX_ROWS"):
            driver().validate_parameters("BAPI_X", {"NOPE": 1}, self.DESCRIBE)

    def test_a_table_parameter_may_be_supplied_as_input(self):
        driver().validate_parameters("BAPI_X", {"FLIGHT_LIST": []}, self.DESCRIBE)

    def test_a_known_path_resolves_to_its_type(self):
        assert driver().resolve_path("BAPI_X", "/FLIGHT_LIST", self.DESCRIBE) == (
            "FLIGHT_LIST",
            FLIGHT_STRUCT,
        )

    def test_a_path_without_the_leading_slash_also_works(self):
        assert driver().resolve_path("BAPI_X", "FLIGHT_LIST", self.DESCRIBE)[0] == "FLIGHT_LIST"

    def test_an_unknown_path_is_a_config_error(self):
        with pytest.raises(Exception, match="FLIGHT_LIST"):
            driver().resolve_path("BAPI_X", "/NOPE", self.DESCRIBE)


class TestReadPlans:
    def test_one_plan_invokes_without_a_path(self):
        # The call must return every result parameter so RETURN can be checked.
        plan = driver().read_plans(None, _obj(), incremental=False, state={})[0]
        assert "sap_rfc_invoke('BAPI_FLIGHT_GETLIST'" in plan.sql
        assert "path" not in plan.sql

    def test_parameters_are_rendered_into_the_call(self):
        plan = driver().read_plans(None, _obj(parameters={"AIRLINE": "LH"}), incremental=False, state={})[0]
        assert "{'AIRLINE': 'LH'}" in plan.sql

    def test_a_function_with_no_parameters_omits_the_struct(self):
        plan = driver().read_plans(None, _obj(parameters={}), incremental=False, state={})[0]
        assert plan.sql == "SELECT * FROM sap_rfc_invoke('BAPI_FLIGHT_GETLIST')"

    def test_slice_by_produces_one_plan_per_value(self):
        d = driver(
            {"name": "flights", "function": "F", "slice_by": {"parameter": "AIRLINE", "values": ["LH", "AA", "UA"]}}
        )
        plans = d.read_plans(
            None, _obj(slice_by={"parameter": "AIRLINE", "values": ["LH", "AA", "UA"]}), incremental=False, state={}
        )
        assert len(plans) == 3
        assert "{'AIRLINE': 'LH'}" in plans[0].sql
        assert plans[0].slice_["AIRLINE"] == "LH"

    def test_a_slice_value_does_not_clobber_a_fixed_parameter(self):
        plans = driver().read_plans(
            None,
            _obj(parameters={"MAX_ROWS": 10}, slice_by={"parameter": "AIRLINE", "values": ["LH"]}),
            incremental=False,
            state={},
        )
        assert "'MAX_ROWS': 10" in plans[0].sql and "'AIRLINE': 'LH'" in plans[0].sql

    def test_incremental_injects_the_state_value_into_the_cursor_parameter(self):
        plan = driver().read_plans(
            None,
            _obj(cursor_field="FLIGHTDATE", cursor_parameter="DATE_FROM"),
            incremental=True,
            state={"FLIGHTDATE": "2026-01-02"},
        )[0]
        assert "'DATE_FROM': '2026-01-02'" in plan.sql

    def test_incremental_without_state_omits_the_cursor_parameter(self):
        plan = driver().read_plans(
            None,
            _obj(cursor_field="FLIGHTDATE", cursor_parameter="DATE_FROM"),
            incremental=True,
            state={},
        )[0]
        assert "DATE_FROM" not in plan.sql


class TestBapiReturnHandling:
    @pytest.mark.parametrize("kind", ["E", "A", "e", "a"])
    def test_error_and_abort_messages_are_failures(self, kind):
        assert is_bapi_failure([{"TYPE": kind, "MESSAGE": "nope"}])

    @pytest.mark.parametrize("kind", ["S", "I", "W", "", None])
    def test_success_info_and_warning_are_not(self, kind):
        assert not is_bapi_failure([{"TYPE": kind, "MESSAGE": "fine"}])

    def test_an_empty_return_table_is_not_a_failure(self):
        assert not is_bapi_failure([])
        assert not is_bapi_failure(None)

    def test_records_from_raises_on_a_bapi_error(self):
        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("FLIGHT_LIST", "x"), ("RETURN", "y")]
        result.fetchone.return_value = (
            [{"AIRLINEID": "LH"}],
            [{"TYPE": "E", "MESSAGE": "Airline LH is unknown", "ID": "BC", "NUMBER": "001"}],
        )
        plan = ReadPlan(sql="x", meta={"path_field": "FLIGHT_LIST", "function": "BAPI_X"})
        with pytest.raises(Exception, match="Airline LH is unknown"):
            list(driver().records_from(plan, cursor))

    def test_records_from_yields_the_path_rows_on_success(self):
        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("FLIGHT_LIST", "x"), ("RETURN", "y")]
        result.fetchone.return_value = ([{"AIRLINEID": "LH"}, {"AIRLINEID": "AA"}], [])
        plan = ReadPlan(sql="x", meta={"path_field": "FLIGHT_LIST", "function": "BAPI_X"})
        assert list(driver().records_from(plan, cursor)) == [{"AIRLINEID": "LH"}, {"AIRLINEID": "AA"}]

    def test_without_a_path_the_scalar_exports_are_one_record(self):
        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("ECHOTEXT", "x"), ("RESPTEXT", "y")]
        result.fetchone.return_value = ("hello", "SAP R/3")
        plan = ReadPlan(sql="x", meta={"path_field": None, "function": "STFC_CONNECTION"})
        assert list(driver().records_from(plan, cursor)) == [{"ECHOTEXT": "hello", "RESPTEXT": "SAP R/3"}]

    def test_values_are_coerced_for_json(self):
        import datetime
        from decimal import Decimal

        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("T", "x"), ("RETURN", "y")]
        result.fetchone.return_value = (
            [{"D": datetime.date(2026, 1, 2), "P": Decimal("1.50")}],
            [],
        )
        plan = ReadPlan(sql="x", meta={"path_field": "T", "function": "F"})
        assert list(driver().records_from(plan, cursor)) == [{"D": "2026-01-02", "P": "1.50"}]

    def test_a_call_that_returns_no_row_yields_nothing(self):
        cursor = MagicMock()
        cursor.execute.return_value.description = [("T", "x")]
        cursor.execute.return_value.fetchone.return_value = None
        plan = ReadPlan(sql="x", meta={"path_field": "T", "function": "F"})
        assert list(driver().records_from(plan, cursor)) == []


class TestNoPatternDiscovery:
    def test_an_empty_object_list_is_a_config_error(self):
        # There is deliberately no pattern discovery: it would mean invoking
        # function modules to find out what they do.
        with pytest.raises(Exception, match="objects"):
            driver().discover(MagicMock())

    def test_an_object_without_a_function_is_a_config_error(self):
        with pytest.raises(Exception, match="function"):
            driver({"name": "x"}).discover(MagicMock())


class TestParameterTyping:
    """SAP checks parameter types, so JSON strings need casting on the way in.

    A config is JSON, so a date arrives as a string; SAP then refuses it with
    "Parameter 'FLIGHTDATE' is of type 'RFCTYPE_DATE' (RFC) but argument is of
    type 'VARCHAR' (DuckDB)". The declared type from `sap_rfc_describe_function`
    is what resolves it.
    """

    TYPES = {
        "FLIGHTDATE": "DATE",
        "DEPTIME": "TIME",
        "MAX_ROWS": "BIGINT",
        "PRICE": "DECIMAL(23,4)",
        "AIRLINE": "VARCHAR",
        "STAMP": "TIMESTAMP",
    }

    def _render(self, parameters):
        return RfcInvokeDriver.render_parameters(parameters, self.TYPES)

    def test_a_sap_date_string_becomes_a_date(self):
        assert "'FLIGHTDATE': DATE '2026-01-02'" in self._render({"FLIGHTDATE": "20260102"})

    def test_an_iso_date_is_accepted_too(self):
        assert "'FLIGHTDATE': DATE '2026-01-02'" in self._render({"FLIGHTDATE": "2026-01-02"})

    def test_a_sap_time_string_becomes_a_time(self):
        assert "'DEPTIME': TIME '10:30:00'" in self._render({"DEPTIME": "103000"})

    def test_an_iso_time_is_accepted_too(self):
        assert "'DEPTIME': TIME '10:30:00'" in self._render({"DEPTIME": "10:30:00"})

    def test_a_numeric_string_is_cast(self):
        assert "'MAX_ROWS': 100::BIGINT" in self._render({"MAX_ROWS": "100"})

    def test_a_real_number_stays_a_number(self):
        assert "'MAX_ROWS': 100::BIGINT" in self._render({"MAX_ROWS": 100})

    def test_a_decimal_is_cast_with_its_precision(self):
        assert "'PRICE': '1.50'::DECIMAL(23,4)" in self._render({"PRICE": "1.50"})

    def test_a_varchar_parameter_is_left_alone(self):
        assert self._render({"AIRLINE": "LH"}) == "{'AIRLINE': 'LH'}"

    def test_an_unknown_parameter_type_is_left_alone(self):
        assert RfcInvokeDriver.render_parameters({"X": "y"}, {}) == "{'X': 'y'}"

    def test_null_survives_typing(self):
        assert self._render({"FLIGHTDATE": None}) == "{'FLIGHTDATE': NULL}"

    def test_an_unparseable_date_is_a_config_error(self):
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        with pytest.raises(AirbyteTracedException, match="FLIGHTDATE"):
            self._render({"FLIGHTDATE": "not-a-date"})

    def test_nested_structures_are_not_cast(self):
        # Only top-level parameters carry a declared type; struct members are
        # rendered as-is, which is what SAP's structure mapping expects.
        got = self._render({"AIRLINE": {"ID": "LH"}})
        assert got == "{'AIRLINE': {'ID': 'LH'}}"

    def test_a_hostile_value_still_cannot_escape(self):
        got = RfcInvokeDriver.render_parameters({"AIRLINE": "x'); DROP TABLE y; --"}, self.TYPES)
        assert got.count("'") % 2 == 0


class TestALowercaseReturnTable:
    """`is_bapi_failure` reads BAPIRET fields case-insensitively; the message
    reader did not, so a driver that lowercases its column names produced
    "F reported an error: " -- the SAP message, which is the entire point of
    checking RETURN, dropped on the floor."""

    def test_the_sap_message_survives(self):
        from source_sap.protocols.rfc_invoke import describe_failure

        described = describe_failure([{"type": "E", "message": "Booking is locked", "id": "BC", "number": "007"}])
        assert "Booking is locked" in described

    def test_the_message_identity_survives(self):
        from source_sap.protocols.rfc_invoke import describe_failure

        described = describe_failure([{"type": "E", "message": "broke", "id": "BC", "number": "007"}])
        assert "BC/007" in described

    def test_uppercase_still_works(self):
        from source_sap.protocols.rfc_invoke import describe_failure

        assert "broke" in describe_failure([{"TYPE": "E", "MESSAGE": "broke"}])

    def test_a_success_row_is_not_described(self):
        from source_sap.protocols.rfc_invoke import describe_failure

        assert describe_failure([{"type": "S", "message": "fine"}]) == ""

    def test_the_two_readers_agree(self):
        from source_sap.protocols.rfc_invoke import describe_failure, is_bapi_failure

        table = [{"type": "E", "message": "broke"}]
        assert is_bapi_failure(table) and describe_failure(table), (
            "a table classified as a failure must produce a description of it"
        )
