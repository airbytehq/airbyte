"""The medium-severity half of crew round 1."""

from unittest.mock import MagicMock

import pytest

from source_sap.protocols.bics import BicsDriver
from source_sap.protocols.rfc_invoke import RfcInvokeDriver, is_sap_type_safe

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


class TestSapTypeStringsAreValidated:
    """F10: type strings from SAP are interpolated into SQL.

    Not a user-input hole -- config goes through sql_string_literal -- but the
    DDIC metadata is trusted, and the RFC transport is unencrypted by default.
    Cheap to close.
    """

    @pytest.mark.parametrize(
        "declared",
        [
            "VARCHAR",
            "DATE",
            "TIME",
            "DECIMAL(23,4)",
            "BIGINT",
            "TIMESTAMP",
            "STRUCT(A VARCHAR, B DATE)",
            "STRUCT(A VARCHAR)[]",
            'STRUCT("TYPE" VARCHAR, ID VARCHAR)',
        ],
    )
    def test_real_sap_types_are_accepted(self, declared):
        assert is_sap_type_safe(declared)

    @pytest.mark.parametrize(
        "hostile",
        [
            "VARCHAR; DROP TABLE x",
            "VARCHAR' OR '1'='1",
            "STRUCT(A VARCHAR); ATTACH 'evil.db'",
            "VARCHAR--comment",
            "VARCHAR/*x*/",
        ],
    )
    def test_anything_with_sql_syntax_is_refused(self, hostile):
        assert not is_sap_type_safe(hostile)

    def test_an_unsafe_type_fails_the_schema_build(self):
        import duckdb
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        con = duckdb.connect()
        with pytest.raises(AirbyteTracedException, match="unexpected"):
            RfcInvokeDriver.schema_for_duckdb_type(con, "STRUCT(A VARCHAR); DROP TABLE x")
        con.close()


class TestBicsIncrementalNeedsAKey:
    """F11: without a primary key the platform cannot dedupe the GE boundary.

    The watermark selects `>= last`, so the boundary period is re-read every
    run; append+dedup handles that only if the stream declares a key.
    """

    def _driver(self, **obj):
        return BicsDriver({**CONN, "protocol": {"mode": "bics", "objects": [{"name": "Q", "cube": "C", **obj}]}})

    def test_a_cursor_variable_without_a_primary_key_is_refused(self):
        with pytest.raises(Exception, match="primary_key"):
            self._driver(cursor_variable="ZV", cursor_field="0CALMONTH").check_incremental_config()

    def test_a_cursor_variable_with_a_primary_key_is_fine(self):
        self._driver(
            cursor_variable="ZV", cursor_field="0CALMONTH", primary_key=["0CALMONTH", "0MATERIAL"]
        ).check_incremental_config()

    def test_full_refresh_objects_need_no_key(self):
        self._driver().check_incremental_config()


class TestDriverIsRequiredOnAPartition:
    """F16: a partition without a driver used to fail deep inside read()."""

    def test_building_a_partition_without_a_driver_is_a_programming_error(self):
        from source_sap.protocols.base import ReadPlan
        from source_sap.streams import ErplPartition

        with pytest.raises(TypeError):
            ErplPartition("S", MagicMock(), ReadPlan(sql="x"), None)


class TestScalarExportsAreProjected:
    """F17: the no-path record was built from whatever came back, not from the
    fields discovery promised, so the schema and the records could disagree."""

    def _driver(self):
        return RfcInvokeDriver(
            {**CONN, "protocol": {"mode": "rfc_invoke", "objects": [{"name": "x", "function": "F"}]}}
        )

    def test_only_the_discovered_export_fields_are_emitted(self):
        from source_sap.protocols.base import ReadPlan

        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("ECHOTEXT", "x"), ("RESPTEXT", "y"), ("SURPRISE", "z")]
        result.fetchone.return_value = ("a", "b", "c")
        plan = ReadPlan(sql="x", meta={"function": "F", "path_field": None, "export_fields": ["ECHOTEXT", "RESPTEXT"]})
        assert list(self._driver().records_from(plan, cursor)) == [{"ECHOTEXT": "a", "RESPTEXT": "b"}]

    def test_without_a_declared_field_list_everything_scalar_is_kept(self):
        from source_sap.protocols.base import ReadPlan

        cursor = MagicMock()
        result = cursor.execute.return_value
        result.description = [("A", "x"), ("B", "y")]
        result.fetchone.return_value = ("1", "2")
        plan = ReadPlan(sql="x", meta={"function": "F", "path_field": None})
        assert list(self._driver().records_from(plan, cursor)) == [{"A": "1", "B": "2"}]
