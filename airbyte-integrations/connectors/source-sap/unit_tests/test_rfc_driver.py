"""RFC driver: object selection, projection/filter pushdown, partitioning."""

import pytest

from source_sap.protocols.base import sql_string_literal
from source_sap.protocols.rfc import RfcDriver


def driver(**protocol):
    return RfcDriver(
        {
            "ashost": "h",
            "sysnr": "00",
            "client": "001",
            "user": "u",
            "password": "p",
            "protocol": {"mode": "rfc", **protocol},
        }
    )


class TestSqlStringLiteral:
    def test_single_quotes_are_escaped(self):
        assert sql_string_literal("O'BRIEN") == "'O''BRIEN'"

    def test_injection_attempt_stays_inside_the_literal(self):
        assert sql_string_literal("X'); DROP TABLE Y; --") == "'X''); DROP TABLE Y; --'"


class TestReadPlans:
    def _obj(self, **meta):
        from source_sap.protocols.base import SapObject

        return SapObject(name=meta.get("name", "SFLIGHT"), json_schema={}, meta={"table": "SFLIGHT", **meta})

    def test_simple_full_refresh_is_one_plan(self):
        plans = driver().read_plans(None, self._obj(), incremental=False, state={})
        assert len(plans) == 1
        assert "sap_read_table('SFLIGHT'" in plans[0].sql

    def test_column_projection_is_pushed_down(self):
        d = driver(objects=[{"name": "SFLIGHT", "columns": ["CARRID", "FLDATE"]}])
        sql = d.read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "COLUMNS := ['CARRID', 'FLDATE']" in sql

    def test_sap_side_filter_is_pushed_down(self):
        d = driver(objects=[{"name": "SFLIGHT", "filter": "CARRID = 'LH'"}])
        sql = d.read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "FILTER := 'CARRID = ''LH'''" in sql

    def test_partitions_and_fetch_size_are_applied(self):
        d = driver(objects=[{"name": "SFLIGHT", "partitions": 8, "fetch_size": 65536}])
        sql = d.read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "PARTITIONS := 8" in sql
        assert "FETCH_SIZE := 65536" in sql

    def test_max_rows_is_applied(self):
        d = driver(objects=[{"name": "SFLIGHT", "max_rows": 100}])
        assert "MAX_ROWS := 100" in d.read_plans(None, self._obj(), incremental=False, state={})[0].sql

    def test_incremental_appends_a_cursor_predicate(self):
        d = driver(objects=[{"name": "SFLIGHT", "cursor_field": "FLDATE"}])
        obj = self._obj(cursor_field="FLDATE")
        sql = d.read_plans(None, obj, incremental=True, state={"FLDATE": "20260101"})[0].sql
        # The predicate is an ABAP WHERE fragment inside a DuckDB string literal,
        # so every quote is doubled once on the way in.
        assert sql == ("SELECT * FROM sap_read_table('SFLIGHT', FILTER := 'FLDATE >= ''20260101''', PARTITIONS := 0)")

    def test_incremental_without_prior_state_reads_everything(self):
        d = driver(objects=[{"name": "SFLIGHT", "cursor_field": "FLDATE"}])
        sql = d.read_plans(None, self._obj(cursor_field="FLDATE"), incremental=True, state={})[0].sql
        assert "FILTER" not in sql

    def test_cursor_predicate_and_user_filter_are_combined(self):
        d = driver(objects=[{"name": "SFLIGHT", "cursor_field": "FLDATE", "filter": "CARRID = 'LH'"}])
        sql = d.read_plans(None, self._obj(cursor_field="FLDATE"), incremental=True, state={"FLDATE": "20260101"})[
            0
        ].sql
        assert "CARRID = ''LH''" in sql and "FLDATE >= ''20260101''" in sql and " AND " in sql

    def test_cursor_value_is_escaped(self):
        d = driver(objects=[{"name": "SFLIGHT", "cursor_field": "FLDATE"}])
        sql = d.read_plans(None, self._obj(cursor_field="FLDATE"), incremental=True, state={"FLDATE": "x' OR '1'='1"})[
            0
        ].sql
        # Every attacker quote is doubled twice over, so the payload stays
        # inside the FILTER literal and cannot close it.
        assert "FILTER := 'FLDATE >= ''x'''' OR ''''1''''=''''1'''" in sql
        assert sql.count("'") % 2 == 0


class TestPatternDefaults:
    def test_pattern_defaults_to_match_nothing_dangerous(self):
        # Discovering every table in an SAP system is a multi-hour operation;
        # require an explicit pattern rather than defaulting to '*'.
        with pytest.raises(Exception) as exc:
            driver().discover(None)
        assert "pattern" in str(exc.value).lower() or "objects" in str(exc.value).lower()


class TestCursorLiteralFormatting:
    """State holds JSON values; SAP's WHERE clause wants ABAP literals."""

    def _obj(self, sap_type):
        from source_sap.protocols.base import SapObject

        return SapObject(
            name="SFLIGHT",
            json_schema={},
            meta={"table": "SFLIGHT", "cursor_field": "FLDATE", "cursor_sap_type": sap_type},
        )

    def _sql(self, sap_type, value):
        d = driver(objects=[{"name": "SFLIGHT", "cursor_field": "FLDATE"}])
        return d.read_plans(None, self._obj(sap_type), incremental=True, state={"FLDATE": value})[0].sql

    def test_dats_loses_its_iso_dashes(self):
        # SAP rejects '2026-09-05' with "is not a valid value for D(8,0)".
        assert "FLDATE >= ''20260905''" in self._sql("DATS", "2026-09-05")

    def test_dats_already_in_sap_form_is_untouched(self):
        assert "FLDATE >= ''20260905''" in self._sql("DATS", "20260905")

    def test_tims_loses_its_colons(self):
        assert "FLDATE >= ''130405''" in self._sql("TIMS", "13:04:05")

    def test_utclong_becomes_a_sap_timestamp(self):
        assert "FLDATE >= ''20260905130405''" in self._sql("UTCLONG", "2026-09-05T13:04:05")

    def test_character_types_pass_through(self):
        assert "FLDATE >= ''LH''" in self._sql("CHAR", "LH")

    def test_unknown_type_passes_through(self):
        assert "FLDATE >= ''abc''" in self._sql(None, "abc")
