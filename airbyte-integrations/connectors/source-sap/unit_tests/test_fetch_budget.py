"""The fetch budget is bytes, and erpl divides it across partition workers.

Measured on a 55-column table: a serial scan gets ~107 rows per RFC round trip,
eight partitions with the default budget get ~17, and the round-trip count goes
up 6.3x. Multiplying the budget by the worker count restores ~94 rows per call,
most of the serial figure. Asking for partitions without also raising the budget
is a footgun, so the connector scales it.

That is a round-trip count, from `bin/trace-round-trips.py`. It is not a claim
about end-to-end throughput, which docs/performance.md reports as still slower
than serial, for reasons this connector has not established.
"""

from source_sap.protocols.base import SapObject
from source_sap.protocols.rfc import DEFAULT_FETCH_SIZE, RfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def sql_for(**obj):
    driver = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", **obj}]}})
    target = SapObject(name="T", json_schema={}, meta={"table": "T"})
    return driver.read_plans(None, target, incremental=False, state={})[0].sql


class TestBudgetScalesWithPartitions:
    def test_a_serial_scan_does_not_state_a_budget(self):
        # Nothing is divided, so erpl's own default is right.
        assert "FETCH_SIZE" not in sql_for(partitions=0)

    def test_partitioning_scales_the_budget_by_the_worker_count(self):
        assert f"FETCH_SIZE := {DEFAULT_FETCH_SIZE * 8}" in sql_for(partitions=8)

    def test_two_partitions_get_twice_the_budget(self):
        assert f"FETCH_SIZE := {DEFAULT_FETCH_SIZE * 2}" in sql_for(partitions=2)

    def test_an_explicit_budget_is_respected(self):
        # The user asked for a number; do not second-guess it.
        assert "FETCH_SIZE := 4096" in sql_for(partitions=8, fetch_size=4096)

    def test_the_scaled_budget_stays_within_its_clamp(self):
        from source_sap.protocols.rfc import MAX_FETCH_SIZE

        assert f"FETCH_SIZE := {MAX_FETCH_SIZE}" in sql_for(partitions=64)

    def test_scaling_applies_to_the_protocol_level_setting_too(self):
        driver = RfcDriver({**CONN, "protocol": {"mode": "rfc", "partitions": 4}})
        target = SapObject(name="T", json_schema={}, meta={"table": "T"})
        sql = driver.read_plans(None, target, incremental=False, state={})[0].sql
        assert f"FETCH_SIZE := {DEFAULT_FETCH_SIZE * 4}" in sql


class TestABudgetThatWouldStarveTheWorkers:
    """`fetch_size: 0` used to clamp up to a one-byte budget, not to nothing."""

    def test_a_zero_budget_means_unset_not_one_byte(self):
        assert "FETCH_SIZE" not in sql_for(partitions=0, fetch_size=0)

    def test_a_zero_budget_still_lets_partitioning_scale(self):
        assert f"FETCH_SIZE := {DEFAULT_FETCH_SIZE * 4}" in sql_for(partitions=4, fetch_size=0)

    def test_an_explicit_budget_too_small_to_divide_is_warned_about(self, caplog):
        sql_for(partitions=8, fetch_size=4096)
        assert "4096" in caplog.text and "8" in caplog.text

    def test_a_generous_explicit_budget_is_not_warned_about(self, caplog):
        sql_for(partitions=8, fetch_size=DEFAULT_FETCH_SIZE * 8)
        assert caplog.text == ""

    def test_a_small_budget_without_partitions_is_not_warned_about(self, caplog):
        # Nothing is divided, so a small budget is just a small budget.
        sql_for(partitions=0, fetch_size=4096)
        assert caplog.text == ""
