"""Remaining guards from the crew review."""

import logging

import pytest

from source_sap.protocols.base import ProtocolDriver
from source_sap.protocols.odp_odata import OdpODataDriver
from source_sap.protocols.odp_rfc import OdpRfcDriver
from source_sap.protocols.rfc import RfcDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


class TestSubscriberCollisionBetweenConfiguredObjects:
    def test_two_objects_sharing_one_subscriber_process_are_refused(self):
        # They would share a single ODQ subscription and interleave their deltas.
        d = OdpRfcDriver(
            {
                **CONN,
                "protocol": {
                    "mode": "odp_rfc",
                    "context": "BW",
                    "objects": [
                        {"name": "A", "subscriber_process": "AB_SHARED"},
                        {"name": "B", "subscriber_process": "AB_SHARED"},
                    ],
                },
            }
        )
        with pytest.raises(Exception, match="AB_SHARED"):
            d.assert_no_subscriber_collisions()

    def test_distinct_names_are_fine(self):
        d = OdpRfcDriver(
            {
                **CONN,
                "protocol": {
                    "mode": "odp_rfc",
                    "context": "BW",
                    "objects": [
                        {"name": "A", "subscriber_process": "AB_ONE"},
                        {"name": "B", "subscriber_process": "AB_TWO"},
                    ],
                },
            }
        )
        d.assert_no_subscriber_collisions()

    def test_derived_names_do_not_collide_between_objects(self):
        d = OdpRfcDriver(
            {**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", "objects": [{"name": "A"}, {"name": "B"}]}}
        )
        d.assert_no_subscriber_collisions()


class TestTuningKnobsAreClamped:
    """A hand-edited config should not be able to overwhelm the SAP system."""

    def _sql(self, **override):
        from source_sap.protocols.base import SapObject

        d = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": [{"name": "T", **override}]}})
        return d.read_plans(
            None, SapObject(name="T", json_schema={}, meta={"table": "T"}), incremental=False, state={}
        )[0].sql

    def test_partitions_are_capped(self):
        assert "PARTITIONS := 64" in self._sql(partitions=10_000)

    def test_partitions_cannot_go_negative(self):
        assert "PARTITIONS := 0" in self._sql(partitions=-3)

    def test_threads_are_capped(self):
        assert "THREADS := 32" in self._sql(threads=9999)

    def test_a_reasonable_value_is_untouched(self):
        assert "PARTITIONS := 8" in self._sql(partitions=8)

    def test_odp_threads_are_capped(self):
        from source_sap.protocols.base import SapObject

        d = OdpRfcDriver(
            {**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", "threads": 9999, "objects": [{"name": "N"}]}}
        )
        obj = SapObject(
            name="BW/N", json_schema={}, meta={"context": "BW", "odp_name": "N", "subscriber_process": "AB_X"}
        )
        assert "THREADS := 32" in d.read_plans(None, obj, incremental=False, state={})[0].sql

    def test_odata_page_size_is_capped(self):
        from source_sap.protocols.base import SapObject

        d = OdpODataDriver(
            {
                "base_url": "https://h",
                "user": "u",
                "password": "p",
                "protocol": {"mode": "odp_odata", "max_page_size": 10_000_000, "objects": [{"url": "/x"}]},
            }
        )
        obj = SapObject(name="x", json_schema={}, meta={"entity_set_url": "https://h/x", "entity_set": "x"})
        assert "max_page_size := 100000" in d.read_plans(None, obj, incremental=False, state={})[0].sql


class TestInsecureTransportWarning:
    def test_a_plaintext_gateway_is_flagged(self, caplog):
        d = OdpODataDriver(
            {"base_url": "http://sap.example.com:8000", "user": "u", "password": "p", "protocol": {"mode": "odp_odata"}}
        )
        with caplog.at_level(logging.WARNING):
            d.warn_about_insecure_transport()
        assert "http" in caplog.text.lower() and "clear" in caplog.text.lower()

    def test_tls_is_not_flagged(self, caplog):
        d = OdpODataDriver(
            {"base_url": "https://sap.example.com", "user": "u", "password": "p", "protocol": {"mode": "odp_odata"}}
        )
        with caplog.at_level(logging.WARNING):
            d.warn_about_insecure_transport()
        assert caplog.text == ""

    def test_rfc_without_snc_is_flagged(self, caplog):
        d = RfcDriver({**CONN, "protocol": {"mode": "rfc"}})
        with caplog.at_level(logging.WARNING):
            d.warn_about_insecure_transport()
        assert "SNC" in caplog.text

    def test_rfc_with_snc_is_not_flagged(self, caplog):
        d = RfcDriver({**CONN, "snc_mode": "1", "protocol": {"mode": "rfc"}})
        with caplog.at_level(logging.WARNING):
            d.warn_about_insecure_transport()
        assert caplog.text == ""


class TestDriverContract:
    def test_prepare_is_declared_on_the_base_class(self):
        # It used to be reached by getattr duck-typing, so a silently-absent hook
        # was indistinguishable from a correctly-absent one.
        assert callable(ProtocolDriver.prepare)

    def test_the_default_prepare_is_a_no_op(self):
        RfcDriver({**CONN, "protocol": {"mode": "rfc"}}).prepare(None, None, {})
