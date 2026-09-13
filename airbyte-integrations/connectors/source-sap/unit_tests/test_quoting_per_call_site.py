"""`sql_string_literal` is the only thing between config and SQL text.

ERPL's table functions take their object names as constants, so these call sites
cannot use bind parameters. Each one gets a hostile input here.
"""

import pytest

from source_sap.protocols.base import SapObject
from source_sap.protocols.bics import BicsDriver
from source_sap.protocols.odp_rfc import OdpRfcDriver
from source_sap.protocols.rfc import RfcDriver

HOSTILE = "X'); DROP TABLE Y; --"
CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


def balanced(sql: str) -> bool:
    """Every quote is paired, so nothing escaped the literal it belongs to."""
    return sql.count("'") % 2 == 0


class TestRfcCallSites:
    def _plan(self, **obj_meta):
        d = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [obj_meta.get("override", {})]}})
        obj = SapObject(name="T", json_schema={}, meta={"table": obj_meta["table"]})
        return d.read_plans(None, obj, incremental=False, state={})[0].sql

    def test_a_hostile_table_name_stays_inside_the_literal(self):
        sql = self._plan(table=HOSTILE)
        assert balanced(sql)
        assert "DROP TABLE Y" in sql  # present, but as data
        assert sql.startswith("SELECT * FROM sap_read_table('")

    def test_a_hostile_column_name_stays_inside_the_list(self):
        d = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", "columns": [HOSTILE]}]}})
        sql = d.read_plans(None, SapObject(name="T", json_schema={}, meta={"table": "T"}), incremental=False, state={})[
            0
        ].sql
        assert balanced(sql)

    def test_a_hostile_filter_stays_inside_the_literal(self):
        d = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", "filter": HOSTILE}]}})
        sql = d.read_plans(None, SapObject(name="T", json_schema={}, meta={"table": "T"}), incremental=False, state={})[
            0
        ].sql
        assert balanced(sql)

    def test_a_realistic_filter_survives_intact(self):
        d = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", "filter": "CARRID = 'LH'"}]}})
        sql = d.read_plans(None, SapObject(name="T", json_schema={}, meta={"table": "T"}), incremental=False, state={})[
            0
        ].sql
        assert balanced(sql)
        assert "FILTER := 'CARRID = ''LH'''" in sql


class TestOdpRfcCallSites:
    def _driver(self, **objects):
        return OdpRfcDriver({**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", **objects}})

    def _obj(self, name="N"):
        return SapObject(
            name=f"BW/{name}", json_schema={}, meta={"context": "BW", "odp_name": name, "subscriber_process": "AB_X"}
        )

    def test_a_hostile_odp_name_stays_inside_the_literal(self):
        sql = self._driver().read_plans(None, self._obj(HOSTILE), incremental=False, state={})[0].sql
        assert balanced(sql)

    def test_a_hostile_context_stays_inside_the_literal(self):
        obj = SapObject(
            name="x", json_schema={}, meta={"context": HOSTILE, "odp_name": "N", "subscriber_process": "AB_X"}
        )
        assert balanced(self._driver().read_plans(None, obj, incremental=False, state={})[0].sql)

    def test_hostile_odp_filters_stay_inside_their_structs(self):
        d = self._driver(objects=[{"name": "N", "filters": [{"fieldname": HOSTILE, "op": "EQ", "low": HOSTILE}]}])
        assert balanced(d.read_plans(None, self._obj(), incremental=False, state={})[0].sql)

    def test_a_hostile_subscriber_process_from_state_is_refused(self):
        # State is attacker-influenced if the platform's state store is; the
        # value goes into the ODQ subscription key on SAP.
        with pytest.raises(Exception, match="subscriber_process"):
            self._driver(objects=[{"name": "N", "subscriber_process": HOSTILE}])._subscriber_for(
                "BW", "N", {"subscriber_process": HOSTILE}
            )


class TestBicsCallSites:
    def _driver(self, **objects):
        return BicsDriver({**CONN, "protocol": {"mode": "bics", **objects}})

    def _obj(self, name="Q"):
        return SapObject(name=name, json_schema={}, meta={"cube": "C", "query": None, "session_id": "s"})

    def test_a_hostile_cube_name_stays_inside_the_literal(self):
        obj = SapObject(name="Q", json_schema={}, meta={"cube": HOSTILE, "query": None, "session_id": "s"})
        for sql in self._driver(objects=[{"name": "Q", "cube": HOSTILE}]).session_statements(obj):
            assert balanced(sql), sql

    def test_hostile_axis_and_filter_members_stay_inside_their_literals(self):
        d = self._driver(
            objects=[
                {
                    "name": "Q",
                    "cube": "C",
                    "rows": [HOSTILE],
                    "columns": [HOSTILE],
                    "filters": [{"characteristic": HOSTILE, "members": [HOSTILE]}],
                }
            ]
        )
        for sql in d.session_statements(self._obj()):
            assert balanced(sql), sql

    def test_hostile_slice_members_stay_inside_their_literals(self):
        d = self._driver(
            objects=[{"name": "Q", "cube": "C", "slice_by": {"characteristic": HOSTILE, "members": [HOSTILE]}}]
        )
        for plan in d.read_plans(None, self._obj(), incremental=False, state={}):
            assert balanced(plan.sql)
            for setup in plan.meta["setup"]:
                assert balanced(setup), setup


class TestTheCursorFieldIsCheckedAtTheSink:
    """Discovery validates the name; `read_plans` is where it reaches SAP.

    The use site falls back to the raw config value when `meta` has no
    `cursor_field`, so a name discovery never saw can reach the ABAP fragment --
    where it cannot be quoted, being an identifier.
    """

    @staticmethod
    def _plans(name):
        from source_sap.protocols.base import SapObject
        from source_sap.protocols.rfc import RfcDriver

        driver = RfcDriver(
            {
                "ashost": "h",
                "sysnr": "00",
                "client": "001",
                "user": "u",
                "password": "p",
                "protocol": {"mode": "rfc", "objects": [{"name": "T", "cursor_field": name}]},
            }
        )
        obj = SapObject(name="T", json_schema={}, supports_incremental=True, meta={"table": "T"})
        return driver.read_plans(None, obj, incremental=True, state={name: "20260101"})

    @pytest.mark.parametrize(
        "hostile",
        ["ERDAT' OR '1'='1", "ERDAT; DROP TABLE", "ERDAT OR 1=1", "E" * 31, "erdat-x"],
    )
    def test_a_field_name_that_is_not_one_is_refused(self, hostile):
        with pytest.raises(Exception) as caught:
            self._plans(hostile)
        assert "cursor_field" in str(caught.value) or "state value" in str(caught.value)

    def test_the_name_that_reaches_sap_is_the_name_that_was_checked(self):
        # Not the raw config spelling: validating one string and sending another
        # is how a check gets bypassed.
        assert "ERDAT >=" in self._plans(" erdat ")[0].sql

    def test_an_empty_name_is_no_cursor_rather_than_an_error(self):
        # Nothing to filter on, so the read is a full one -- not a refusal.
        assert "FILTER" not in self._plans("")[0].sql

    def test_a_real_field_name_still_works(self):
        assert "ERDAT >=" in self._plans("ERDAT")[0].sql
