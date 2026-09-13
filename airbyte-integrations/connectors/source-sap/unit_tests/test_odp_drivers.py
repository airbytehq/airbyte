"""ODP over RFC and ODP over OData: plan construction and state handling."""

from source_sap.protocols.base import SapObject
from source_sap.protocols.odp_odata import OdpODataDriver
from source_sap.protocols.odp_rfc import OdpRfcDriver


def rfc_driver(**protocol):
    return OdpRfcDriver(
        {
            "ashost": "h",
            "sysnr": "00",
            "client": "001",
            "user": "u",
            "password": "p",
            "protocol": {"mode": "odp_rfc", **protocol},
        }
    )


def odata_driver(**protocol):
    return OdpODataDriver(
        {"base_url": "http://sap:50000", "user": "u", "password": "p", "protocol": {"mode": "odp_odata", **protocol}}
    )


class TestOdpRfcPlans:
    def _obj(self, **meta):
        return SapObject(
            name="ABAP_CDS/ZV$F",
            json_schema={},
            supports_incremental=True,
            change_mode_field="ODQ_CHANGEMODE",
            meta={"context": "ABAP_CDS", "odp_name": "ZV$F", **meta},
        )

    def test_full_refresh_uses_read_full(self):
        sql = rfc_driver().read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "sap_odp_read_full('ABAP_CDS', 'ZV$F'" in sql

    def test_incremental_uses_read_delta_with_the_subscriber_process(self):
        d = rfc_driver()
        plans = d.read_plans(None, self._obj(subscriber_process="AB_X"), incremental=True, state={})
        assert "sap_odp_read_delta('ABAP_CDS', 'ZV$F', 'AB_X')" in plans[0].sql

    def test_delta_is_never_parallelised(self):
        # erpl caps delta fetch to one thread; asking for more races the pointer.
        sql = (
            rfc_driver(threads=8)
            .read_plans(None, self._obj(subscriber_process="AB_X"), incremental=True, state={})[0]
            .sql
        )
        assert "THREADS" not in sql.upper()

    def test_full_refresh_honours_threads(self):
        sql = rfc_driver(threads=8).read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "THREADS := 8" in sql

    def test_state_records_the_subscriber_process(self):
        d = rfc_driver()
        state = d.next_state(None, self._obj(subscriber_process="AB_X"), {})
        assert state["subscriber_process"] == "AB_X"
        assert state["initialized"] is True


class TestOdpODataPlans:
    def _obj(self, **meta):
        return SapObject(
            name="FactsOfZ",
            json_schema={},
            supports_incremental=True,
            change_mode_field="ODQ_CHANGEMODE",
            meta={"entity_set_url": "http://sap:50000/srv/FactsOfZ", "entity_set": "FactsOfZ", **meta},
        )

    def test_read_binds_the_url_as_a_parameter(self):
        plan = odata_driver().read_plans(None, self._obj(), incremental=False, state={})[0]
        assert "odp_odata_read(?" in plan.sql
        assert plan.params[0] == "http://sap:50000/srv/FactsOfZ"

    def test_full_refresh_forces_a_full_load(self):
        sql = odata_driver().read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "force_full_load := true" in sql

    def test_incremental_does_not_force_a_full_load(self):
        sql = odata_driver().read_plans(None, self._obj(), incremental=True, state={"delta_token": "D1"})[0].sql
        assert "force_full_load" not in sql

    def test_max_page_size_is_applied(self):
        sql = odata_driver(max_page_size=5000).read_plans(None, self._obj(), incremental=False, state={})[0].sql
        assert "max_page_size := 5000" in sql


class TestOdpODataStateSeeding:
    def test_seed_writes_into_erpl_webs_own_table(self):
        statements = OdpODataDriver.seed_subscription_statements(
            "http://sap:50000/srv/FactsOfZ", "FactsOfZ", "D20260101_1"
        )
        assert any("erpl_web.odp_subscriptions" in sql for sql, _ in statements)

    def test_the_existing_row_is_deleted_before_inserting(self):
        # odp_subscriptions has a PRIMARY KEY *and* a UNIQUE(service_url,
        # entity_set_name); DuckDB refuses INSERT OR REPLACE on a table with
        # more than one unique constraint.
        statements = OdpODataDriver.seed_subscription_statements("http://sap:50000/srv/FactsOfZ", "FactsOfZ", "D1")
        kinds = [sql.strip().split()[0].upper() for sql, _ in statements]
        assert kinds == ["DELETE", "INSERT"]
        assert "OR REPLACE" not in " ".join(sql for sql, _ in statements)

    def test_the_delete_matches_the_unique_key_not_the_id(self):
        # subscription_id is timestamp-prefixed and unstable across runs.
        (delete_sql, delete_params), _ = OdpODataDriver.seed_subscription_statements(
            "http://sap:50000/srv/FactsOfZ", "FactsOfZ", "D1"
        )
        assert "service_url = ?" in delete_sql and "entity_set_name = ?" in delete_sql
        assert list(delete_params) == ["http://sap:50000/srv/FactsOfZ", "FactsOfZ"]

    def test_values_are_never_interpolated(self):
        statements = OdpODataDriver.seed_subscription_statements(
            "http://sap:50000/srv/FactsOfZ", "FactsOfZ", "D20260101_1"
        )
        for sql, _ in statements:
            assert "D20260101_1" not in sql
        assert any("D20260101_1" in list(params) for _, params in statements)


class TestOdpRfcCursorCleanup:
    """`release` runs before `next_state`, so on the first run state is empty."""

    def _obj(self):
        return SapObject(
            name="ABAP_CDS/ZV$F",
            json_schema={},
            supports_incremental=True,
            meta={"context": "ABAP_CDS", "odp_name": "ZV$F", "subscriber_process": "AB_X"},
        )

    def _session(self):
        from unittest.mock import MagicMock

        session = MagicMock()
        session.cursor.return_value.execute.return_value.fetchone.return_value = ("CLOSED",)
        return session

    def test_the_cursor_is_closed_on_the_first_run_with_empty_state(self):
        # The first DELTAINIT would otherwise leave a delta cursor reserved on SAP.
        session = self._session()
        rfc_driver().release(session, self._obj(), {})
        sql = session.cursor.return_value.execute.call_args[0][0]
        assert "sap_odp_close_delta_cursor" in sql
        assert "'AB_X'" in sql

    def test_state_wins_over_the_derived_name(self):
        session = self._session()
        rfc_driver().release(session, self._obj(), {"subscriber_process": "AB_FROM_STATE"})
        assert "'AB_FROM_STATE'" in session.cursor.return_value.execute.call_args[0][0]

    def test_nothing_is_closed_when_there_is_no_subscriber_at_all(self):
        session = self._session()
        obj = SapObject(name="x", json_schema={}, meta={"context": "C", "odp_name": "N"})
        rfc_driver().release(session, obj, {})
        session.cursor.return_value.execute.assert_not_called()
