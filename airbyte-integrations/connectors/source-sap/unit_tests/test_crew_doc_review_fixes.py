"""Fixes from the documentation review, which found code defects as well as
documentation ones."""

import logging

import pytest

from source_sap.source import SourceSap

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}


class TestInsecureTransportIsActuallyWarnedAbout:
    """The hook, its override and its unit tests all existed; nothing called it.

    The documentation promised a warning when the password travels in the clear,
    which is the one claim in that page a reader might rely on.
    """

    def test_check_warns_when_snc_is_off(self, caplog, monkeypatch):
        driver_calls = []

        class _Session:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        monkeypatch.setattr(SourceSap, "_new_session", lambda self, c, d: _Session())

        class _Driver:
            required_extensions = ()

            def __init__(self, config):
                self.config = config

            def warn_about_insecure_transport(self):
                driver_calls.append("warned")

            def check(self, session):
                return "ok"

        monkeypatch.setattr(SourceSap, "_driver", lambda self, c: _Driver(c))
        with caplog.at_level(logging.WARNING):
            SourceSap().check_connection(logging.getLogger("airbyte"), {**CONN, "protocol": {"mode": "rfc"}})
        assert driver_calls == ["warned"], "check must warn about an unencrypted transport"

    def test_the_real_rfc_driver_warns(self, caplog):
        from source_sap.protocols.rfc import RfcDriver

        with caplog.at_level(logging.WARNING):
            RfcDriver({**CONN, "protocol": {"mode": "rfc"}}).warn_about_insecure_transport()
        assert "SNC" in caplog.text


class TestSpecExposesWhatTheCodeRequires:
    """A setting the code needs but the form does not offer is unreachable."""

    def _branch(self, mode):
        import yaml

        spec = yaml.safe_load(open("source_sap/spec.yaml"))
        return next(
            b
            for b in spec["connectionSpecification"]["properties"]["protocol"]["oneOf"]
            if b["properties"]["mode"]["const"] == mode
        )

    def test_bics_objects_offer_a_primary_key(self):
        # BICS incremental *requires* one, so without this the feature cannot be
        # configured from the Airbyte UI at all.
        items = self._branch("bics")["properties"]["objects"]["items"]["properties"]
        assert "primary_key" in items

    @pytest.mark.parametrize("mode", ["rfc", "rfc_invoke", "bics", "odp_rfc", "odp_odata"])
    def test_every_object_list_offers_a_primary_key(self, mode):
        items = self._branch(mode)["properties"]["objects"]["items"]["properties"]
        assert "primary_key" in items, f"{mode} objects cannot declare a key"

    def test_fetch_size_is_described_as_bytes(self):
        # It said "Rows requested per SAP round trip", which is the wrong unit
        # and led every reader of the form to size it against their row count.
        text = self._branch("rfc")["properties"]["fetch_size"]["description"].lower()
        assert "byte" in text
        assert "rows requested" not in text


class TestCdcTombstoneIsInTheSchema:
    """A field absent from the declared schema may be dropped by a typed
    destination, and the tombstone is the reason to choose ODP at all."""

    def test_a_delta_capable_stream_declares_the_tombstone(self):
        from source_sap.protocols.base import SapObject
        from source_sap.streams import CDC_DELETED_AT, declare_cdc_column

        schema = declare_cdc_column(
            {"type": "object", "properties": {"A": {"type": ["null", "string"]}}},
            SapObject(name="s", json_schema={}, supports_incremental=True, change_mode_field="ODQ_CHANGEMODE", meta={}),
        )
        assert CDC_DELETED_AT in schema["properties"]
        assert schema["properties"][CDC_DELETED_AT]["format"] == "date-time"

    def test_a_stream_without_change_tracking_does_not(self):
        from source_sap.protocols.base import SapObject
        from source_sap.streams import CDC_DELETED_AT, declare_cdc_column

        schema = declare_cdc_column(
            {"type": "object", "properties": {}},
            SapObject(name="s", json_schema={}, meta={}),
        )
        assert CDC_DELETED_AT not in schema["properties"]
