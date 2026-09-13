"""An OData entity set that exposes no change-mode column cannot report deletes.

The connector advertises incremental for every `odp_odata` stream, but the CDC
tombstone is conditional on a change-mode column being present. Where there is
none, the stream still offers incremental and no record ever carries
`_ab_cdc_deleted_at` -- so a deleted row simply stops appearing, and the
destination keeps it forever. README and docs/incremental.md promise the
opposite for "both ODP protocols".

Incremental is still offered: an entity set with change tracking off is a
legitimate append-only feed, and refusing it would remove a working sync. What
was missing is that anyone is told.
"""

import logging
from unittest.mock import MagicMock

from source_sap.protocols.odp_odata import OdpODataDriver

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p", "base_url": "https://gw:44300"}


def _driver(**protocol):
    return OdpODataDriver({**CONN, "protocol": {"mode": "odp_odata", **protocol}})


def _session_with_columns(*names):
    session = MagicMock()
    cursor = session.cursor.return_value
    cursor.description = [(n, "VARCHAR", None, None, None, None, None) for n in names]
    return session


def _discover(session, driver=None):
    driver = driver or _driver(objects=[{"entity_set": "E", "url": "/sap/opu/odata/sap/S/E"}])
    return driver.discover(session)


class TestAnEntitySetWithoutAChangeModeColumn:
    def test_is_still_discovered(self, caplog):
        objects = _discover(_session_with_columns("CARRID", "CONNID"))
        assert [o.name for o in objects] == ["E"]

    def test_warns_that_deletes_will_be_invisible(self, caplog):
        with caplog.at_level(logging.WARNING):
            _discover(_session_with_columns("CARRID", "CONNID"))
        assert "delete" in caplog.text.lower(), "nothing told the operator deletes cannot arrive"
        assert "E" in caplog.text

    def test_declares_no_tombstone_in_its_schema(self):
        from source_sap.streams import CDC_DELETED_AT, declare_cdc_column

        obj = _discover(_session_with_columns("CARRID"))[0]
        assert CDC_DELETED_AT not in declare_cdc_column(obj.json_schema, obj)["properties"]


class TestAnEntitySetWithAChangeModeColumn:
    def test_is_not_warned_about(self, caplog):
        with caplog.at_level(logging.WARNING):
            _discover(_session_with_columns("CARRID", "ODQ_CHANGEMODE"))
        assert "delete" not in caplog.text.lower()

    def test_declares_the_tombstone(self):
        from source_sap.streams import CDC_DELETED_AT, declare_cdc_column

        obj = _discover(_session_with_columns("CARRID", "ODQ_CHANGEMODE"))[0]
        assert CDC_DELETED_AT in declare_cdc_column(obj.json_schema, obj)["properties"]
