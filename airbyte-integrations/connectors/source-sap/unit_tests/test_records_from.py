"""The driver contract for turning a read plan into rows.

Most protocols iterate a result set. RFC function invocation cannot: the whole
result of the call is a single row whose columns are the function's result
parameters, and the BAPI `RETURN` table has to be inspected before any of it is
emitted. So the row production is a driver method with a default implementation
rather than something hard-coded in the partition.
"""

from unittest.mock import MagicMock

import pytest

from source_sap.protocols.base import ProtocolDriver, ReadPlan
from source_sap.protocols.rfc import RfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def _cursor(description, batches):
    cursor = MagicMock()
    result = cursor.execute.return_value
    result.description = description
    result.fetchmany.side_effect = [*batches, []]
    return cursor


class TestDefaultRecordsFrom:
    def _driver(self):
        return RfcDriver({**CONN, "protocol": {"mode": "rfc"}})

    def test_rows_become_dicts_keyed_by_column(self):
        cursor = _cursor([("A", "VARCHAR"), ("B", "INTEGER")], [[("x", 1), ("y", 2)]])
        rows = list(self._driver().records_from(ReadPlan(sql="SELECT 1"), cursor))
        assert rows == [{"A": "x", "B": 1}, {"A": "y", "B": 2}]

    def test_values_are_coerced_for_json(self):
        import datetime
        from decimal import Decimal

        cursor = _cursor([("D", "DATE"), ("N", "DECIMAL")], [[(datetime.date(2026, 1, 2), Decimal("1.50"))]])
        (row,) = list(self._driver().records_from(ReadPlan(sql="SELECT 1"), cursor))
        assert row == {"D": "2026-01-02", "N": "1.50"}

    def test_an_empty_result_yields_nothing(self):
        cursor = _cursor([("A", "VARCHAR")], [])
        assert list(self._driver().records_from(ReadPlan(sql="SELECT 1"), cursor)) == []

    def test_bound_parameters_are_passed_through(self):
        cursor = _cursor([("A", "VARCHAR")], [[("x",)]])
        list(self._driver().records_from(ReadPlan(sql="SELECT ?", params=["v"]), cursor))
        cursor.execute.assert_called_once_with("SELECT ?", ["v"])

    def test_setup_statements_run_before_the_query(self):
        # BICS opens a stateful session before the result can be fetched.
        cursor = _cursor([("A", "VARCHAR")], [[("x",)]])
        plan = ReadPlan(sql="SELECT 1", meta={"setup": ["BEGIN ONE", "BEGIN TWO"]})
        list(self._driver().records_from(plan, cursor))
        executed = [c.args[0] for c in cursor.execute.call_args_list]
        assert executed[:2] == ["BEGIN ONE", "BEGIN TWO"]
        assert executed[-1] == "SELECT 1"


class TestContract:
    def test_records_from_is_declared_on_the_base_class(self):
        assert callable(ProtocolDriver.records_from)

    def test_prepare_is_declared_on_the_base_class(self):
        assert callable(ProtocolDriver.prepare)

    def test_a_driver_can_override_record_production(self):
        class Custom(RfcDriver):
            def records_from(self, plan, cursor):
                yield {"custom": True}

        rows = list(Custom({**CONN, "protocol": {"mode": "rfc"}}).records_from(ReadPlan(sql="x"), MagicMock()))
        assert rows == [{"custom": True}]


class TestPartitionUsesTheDriver:
    def test_the_partition_yields_whatever_the_driver_produced(self):
        from source_sap.streams import ErplPartition

        driver = MagicMock()
        driver.records_from.return_value = iter([{"A": 1}, {"A": 2}])
        partition = ErplPartition("S", MagicMock(), ReadPlan(sql="x"), None, driver=driver)
        assert [r.data for r in partition.read()] == [{"A": 1}, {"A": 2}]

    def test_a_driver_failure_still_marks_the_cursor(self):
        from airbyte_cdk.utils.traced_exception import AirbyteTracedException

        from source_sap.streams import ErplPartition

        driver = MagicMock()
        driver.records_from.side_effect = RuntimeError("boom")
        cursor = MagicMock()
        partition = ErplPartition("S", MagicMock(), ReadPlan(sql="x"), None, driver=driver, cursor=cursor)
        with pytest.raises(AirbyteTracedException):
            list(partition.read())
        cursor.mark_failed.assert_called_once()


class TestReadPlanSeparatesMachineryFromSliceKeys:
    """`slice_` is logged as the partition's identity, so driver machinery does
    not belong in it: a BICS setup script or a column list ends up in debug
    output claiming to describe which slice of the stream this is."""

    def test_the_slice_only_carries_slice_keys(self):
        from source_sap.protocols.base import ReadPlan

        plan = ReadPlan(sql="x", slice_={"member": "202601"}, meta={"setup": ["BEGIN"], "path_field": "T"})
        assert plan.slice_ == {"member": "202601"}

    def test_machinery_lives_in_meta(self):
        from source_sap.protocols.base import ReadPlan

        plan = ReadPlan(sql="x", meta={"setup": ["BEGIN"]})
        assert plan.meta["setup"] == ["BEGIN"]

    def test_a_partition_reports_only_the_slice_keys(self):
        from source_sap.protocols.base import ReadPlan
        from source_sap.streams import ErplPartition

        plan = ReadPlan(sql="x", slice_={"member": "202601"}, meta={"setup": ["BEGIN"]})
        partition = ErplPartition("S", MagicMock(), plan, None, driver=MagicMock())
        assert partition.to_slice() == {"member": "202601"}
