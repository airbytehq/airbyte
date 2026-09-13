"""BICS driver: session workflow, variables, and the grand-total row."""

import pytest

from source_sap.protocols.base import SapObject
from source_sap.protocols.bics import BicsDriver, is_grand_total_row


def driver(**protocol):
    return BicsDriver(
        {
            "ashost": "h",
            "sysnr": "00",
            "client": "001",
            "user": "u",
            "password": "p",
            "protocol": {"mode": "bics", **protocol},
        }
    )


class TestGrandTotalRow:
    @pytest.mark.parametrize("value", ["SUMME", "Overall Result", "Gesamtergebnis", "Result"])
    def test_known_total_labels_are_detected(self, value):
        assert is_grand_total_row({"0CALDAY": value, "AMOUNT": 1.0}, ["0CALDAY"])

    def test_ordinary_rows_are_kept(self):
        assert not is_grand_total_row({"0CALDAY": "20260101", "AMOUNT": 1.0}, ["0CALDAY"])

    def test_only_row_axis_columns_are_examined(self):
        # A key figure that happens to be the string "Result" must not drop the row.
        assert not is_grand_total_row({"0CALDAY": "20260101", "TEXT": "Result"}, ["0CALDAY"])


class TestSessionWorkflow:
    def _obj(self, **meta):
        return SapObject(
            name="Q1", json_schema={}, meta={"cube": "MY_CUBE", "query": "Q1", "session_id": "abyte_Q1", **meta}
        )

    def test_begin_binds_variables(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE", "variables": [{"name": "ZVAR_YEAR", "low": "2026"}]}])
        stmts = d.session_statements(self._obj())
        begin = stmts[0]
        assert "sap_bics_begin('MY_CUBE'" in begin
        assert "'NAME': 'ZVAR_YEAR'" in begin
        assert "'LOW': '2026'" in begin

    def test_variable_defaults_to_include_equals(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE", "variables": [{"name": "V", "low": "1"}]}])
        begin = d.session_statements(self._obj())[0]
        assert "'SIGN': 'I'" in begin and "'OP': 'EQ'" in begin

    def test_interval_variable_uses_between(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE", "variables": [{"name": "V", "low": "1", "high": "9"}]}])
        begin = d.session_statements(self._obj())[0]
        assert "'OP': 'BT'" in begin and "'HIGH': '9'" in begin

    def test_rows_and_columns_become_axis_calls(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE", "rows": ["0CALDAY"], "columns": ["0AMOUNT"]}])
        stmts = " | ".join(d.session_statements(self._obj()))
        assert "sap_bics_rows('abyte_Q1', '0CALDAY'" in stmts
        assert "sap_bics_columns('abyte_Q1', '0AMOUNT'" in stmts

    def test_member_filters_become_filter_calls(self):
        d = driver(
            objects=[
                {"name": "Q1", "cube": "MY_CUBE", "filters": [{"characteristic": "0CNTRY", "members": ["DE", "FR"]}]}
            ]
        )
        stmts = " | ".join(d.session_statements(self._obj()))
        assert "sap_bics_filter('abyte_Q1', '0CNTRY', 'DE', 'FR'" in stmts

    def test_result_is_the_last_statement(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE"}])
        assert d.session_statements(self._obj())[-1].startswith("SELECT * FROM sap_bics_result(")

    def test_variable_values_are_escaped(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE", "variables": [{"name": "V", "low": "a' OR '1'='1"}]}])
        begin = d.session_statements(self._obj())[0]
        assert "'LOW': 'a'' OR ''1''=''1'" in begin


class TestSlicing:
    def _obj(self):
        return SapObject(name="Q1", json_schema={}, meta={"cube": "MY_CUBE", "query": "Q1", "session_id": "abyte_Q1"})

    def test_slices_produce_one_plan_each(self):
        # BICS cannot paginate: BW builds the whole result or none of it. Slicing
        # on a characteristic is the only way to bound memory.
        d = driver(
            objects=[
                {
                    "name": "Q1",
                    "cube": "MY_CUBE",
                    "slice_by": {"characteristic": "0CALMONTH", "members": ["202601", "202602", "202603"]},
                }
            ]
        )
        plans = d.read_plans(None, self._obj(), incremental=False, state={})
        assert len(plans) == 3
        assert plans[0].slice_["member"] == "202601"

    def test_without_slicing_there_is_one_plan(self):
        d = driver(objects=[{"name": "Q1", "cube": "MY_CUBE"}])
        assert len(d.read_plans(None, self._obj(), incremental=False, state={})) == 1

    def test_each_slice_gets_its_own_session_id(self):
        d = driver(
            objects=[
                {"name": "Q1", "cube": "MY_CUBE", "slice_by": {"characteristic": "0CALMONTH", "members": ["1", "2"]}}
            ]
        )
        plans = d.read_plans(None, self._obj(), incremental=False, state={})
        ids = {p.meta["session_id"] for p in plans}
        assert len(ids) == 2


class TestSessionIdUniqueness:
    """Each slice runs its own BICS session; colliding ids interleave results."""

    def test_slices_of_a_long_stream_name_keep_distinct_sessions(self):
        # BW technical names routinely run to 30 characters. Truncating after
        # appending the member would give every slice the same session id, and
        # the Concurrent CDK reads slices in parallel.
        long_name = "ZQUERY_WITH_A_VERY_LONG_TECHNICAL_NAME_0001"
        d = driver(
            objects=[
                {
                    "name": long_name,
                    "cube": "C",
                    "slice_by": {"characteristic": "0CALMONTH", "members": ["202601", "202602", "202603"]},
                }
            ]
        )
        from source_sap.protocols.base import SapObject

        obj = SapObject(name=long_name, json_schema={}, meta={"cube": "C", "query": None, "session_id": "x"})
        ids = {p.meta["session_id"] for p in d.read_plans(None, obj, incremental=False, state={})}
        assert len(ids) == 3

    def test_session_ids_stay_within_the_sap_field(self):
        from source_sap.protocols.bics import session_id_for

        got = session_id_for("Z" * 80, "202601")
        assert len(got) <= 40

    def test_session_ids_are_stable(self):
        from source_sap.protocols.bics import session_id_for

        assert session_id_for("Q", "a") == session_id_for("Q", "a")

    def test_different_streams_do_not_collide(self):
        from source_sap.protocols.bics import session_id_for

        assert session_id_for("A" * 60, "") != session_id_for("B" * 60, "")


class TestGrandTotalWithoutARowAxis:
    def test_every_string_column_is_checked_when_no_row_axis_is_known(self):
        # Otherwise a query with no `rows` configured emits the total as a fact.
        assert is_grand_total_row({"0CALDAY": "Overall Result", "AMOUNT": 1.0})

    def test_ordinary_rows_still_pass(self):
        assert not is_grand_total_row({"0CALDAY": "20260101", "AMOUNT": 1.0})

    def test_non_string_cells_are_ignored(self):
        assert not is_grand_total_row({"0CALDAY": None, "AMOUNT": 1.0})


class TestBicsIncremental:
    """BICS has no change tracking, but a BEx variable can carry a watermark.

    A query restricted by a period variable can be re-run with the variable set
    from the highest period seen last time, which is as close to incremental as
    BW gets without an ODP extractor behind it.
    """

    def _obj(self, **meta):
        return SapObject(name="Q", json_schema={}, meta={"cube": "C", "query": "Q", "session_id": "s", **meta})

    def _driver(self, **obj):
        return driver(objects=[{"name": "Q", "cube": "C", **obj}])

    def test_a_cursor_variable_makes_the_stream_incremental(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH")
        assert d.supports_incremental({"cursor_variable": "ZVAR_MONTH", "cursor_field": "0CALMONTH"})

    def test_a_cursor_field_alone_is_not_enough(self):
        # Without a variable there is nothing to restrict the query with, so the
        # "incremental" run would re-read everything and dedupe client-side.
        d = self._driver(cursor_field="0CALMONTH")
        assert not d.supports_incremental({"cursor_field": "0CALMONTH"})

    def test_the_state_value_fills_the_variable(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH")
        stmts = d.session_statements(
            self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"),
            state={"0CALMONTH": "202603"},
        )
        assert "'NAME': 'ZVAR_MONTH'" in stmts[0]
        assert "'LOW': '202603'" in stmts[0]

    def test_the_watermark_uses_a_greater_or_equal_style_selection(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH")
        stmts = d.session_statements(
            self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"),
            state={"0CALMONTH": "202603"},
        )
        # BW's selection options: GE is the watermark shape.
        assert "'OP': 'GE'" in stmts[0]

    def test_without_state_the_configured_start_is_used(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH", cursor_start="202601")
        stmts = d.session_statements(self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"), state={})
        assert "'LOW': '202601'" in stmts[0]

    def test_without_state_or_a_start_the_variable_is_left_unset(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH")
        stmts = d.session_statements(self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"), state={})
        assert "ZVAR_MONTH" not in stmts[0]

    def test_an_explicit_variable_binding_is_not_overwritten(self):
        d = self._driver(
            cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH", variables=[{"name": "ZVAR_REGION", "low": "EU"}]
        )
        stmts = d.session_statements(
            self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"),
            state={"0CALMONTH": "202603"},
        )
        assert "'NAME': 'ZVAR_REGION'" in stmts[0] and "'NAME': 'ZVAR_MONTH'" in stmts[0]

    def test_the_watermark_value_is_escaped(self):
        d = self._driver(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH")
        stmts = d.session_statements(
            self._obj(cursor_variable="ZVAR_MONTH", cursor_field="0CALMONTH"),
            state={"0CALMONTH": "a' OR '1'='1"},
        )
        assert stmts[0].count("'") % 2 == 0


class TestSetupTravelsWithEveryPlan:
    """BICS is stateful: without its setup statements, `sap_bics_result` answers
    "No BICS state found for id". A refactor once moved setup out of the plan for
    the unsliced path only, and every unit test still passed."""

    def _obj(self):
        return SapObject(name="Q", json_schema={}, meta={"cube": "C", "query": "Q", "session_id": "abyte_q"})

    def test_an_unsliced_plan_carries_its_setup(self):
        d = driver(objects=[{"name": "Q", "cube": "C", "rows": ["0CALDAY"]}])
        (plan,) = d.read_plans(None, self._obj(), incremental=False, state={})
        assert plan.meta["setup"], "the session must be opened before the result is read"
        assert any("sap_bics_begin" in s for s in plan.meta["setup"])
        assert plan.sql.startswith("SELECT * FROM sap_bics_result(")

    def test_every_sliced_plan_carries_its_own_setup(self):
        d = driver(
            objects=[
                {"name": "Q", "cube": "C", "slice_by": {"characteristic": "0CALMONTH", "members": ["202601", "202602"]}}
            ]
        )
        plans = d.read_plans(None, self._obj(), incremental=False, state={})
        assert len(plans) == 2
        for plan in plans:
            assert any("sap_bics_begin" in s for s in plan.meta["setup"])

    def test_setup_is_not_reported_as_a_slice_key(self):
        d = driver(objects=[{"name": "Q", "cube": "C"}])
        (plan,) = d.read_plans(None, self._obj(), incremental=False, state={})
        assert "setup" not in plan.slice_


class TestTheGeneratedSqlActuallyParses:
    """Asserting substrings proves we built a string, not a statement.

    The BEx variables block rendered `{'NAME': 'V', ...}`, which is not DuckDB
    struct syntax: it fails at the parser, before reaching SAP. Every test here
    checked for substrings and passed. Parsing the statement is the assertion
    that could have failed.
    """

    @staticmethod
    def _statements(**obj):
        d = driver(objects=[{"name": "Q", "cube": "C", **obj}])
        target = SapObject(name="Q", json_schema={}, meta={"cube": "C", "query": "Q", "session_id": "s"})
        return d.session_statements(target)

    @staticmethod
    def _parses(statement):
        import duckdb

        # EXPLAIN parses and binds without executing; an unknown table function
        # is a binder error, which is not what this is looking for.
        try:
            duckdb.connect().execute(f"EXPLAIN {statement}")
        except Exception as exc:
            message = str(exc)
            if "Parser Error" in message or "syntax error" in message:
                raise AssertionError(f"{message.splitlines()[0]}\n  in: {statement}") from exc

    def test_a_plain_session_parses(self):
        for statement in self._statements():
            self._parses(statement)

    def test_bex_variables_parse(self):
        for statement in self._statements(query="Q", variables=[{"name": "0CALMONTH", "low": "202601"}]):
            self._parses(statement)

    def test_a_ranged_variable_parses(self):
        variables = [{"name": "V", "low": "a", "high": "b", "sign": "I", "op": "BT"}]
        for statement in self._statements(query="Q", variables=variables):
            self._parses(statement)

    def test_rows_columns_and_filters_parse(self):
        statements = self._statements(
            rows=["0CALMONTH"],
            columns=["0AMOUNT"],
            filters=[{"characteristic": "0COMP_CODE", "members": ["1000", "2000"]}],
        )
        for statement in statements:
            self._parses(statement)

    def test_a_variable_still_carries_its_fields(self):
        begin = self._statements(query="Q", variables=[{"name": "0CALMONTH", "low": "202601"}])[0]
        assert "'NAME': '0CALMONTH'" in begin and "'LOW': '202601'" in begin
