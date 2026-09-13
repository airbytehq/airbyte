"""Fixes from the crew review that span several modules."""

import logging

import pytest

from source_sap.errors import config_error  # noqa: F401 - imported for the type it raises
from source_sap.protocols.odp_odata import OdpODataDriver
from source_sap.protocols.rfc import RfcDriver
from source_sap.source import SourceSap


class TestCursorFieldValidation:
    """The cursor field is the one identifier interpolated bare into ABAP."""

    def _driver(self, cursor_field):
        return RfcDriver(
            {
                "ashost": "h",
                "sysnr": "00",
                "client": "001",
                "user": "u",
                "password": "p",
                "protocol": {
                    "mode": "rfc",
                    "table_pattern": "T",
                    "objects": [{"name": "T", "cursor_field": cursor_field}],
                },
            }
        )

    @pytest.mark.parametrize("bad", ["A OR 1=1", "A;B", "a-b", "A'", "A B"])
    def test_an_unusable_cursor_field_is_rejected(self, bad):
        with pytest.raises(Exception, match="cursor_field"):
            self._driver(bad).validate_cursor_field(bad, ["A", "B"])

    def test_a_field_the_table_does_not_have_is_rejected(self):
        with pytest.raises(Exception, match="cursor_field"):
            self._driver("NOPE").validate_cursor_field("NOPE", ["FLDATE", "CARRID"])

    def test_a_discovered_field_is_accepted(self):
        assert self._driver("FLDATE").validate_cursor_field("FLDATE", ["FLDATE"]) == "FLDATE"


class TestOdataUrlIsConfinedToTheGateway:
    """An absolute entity-set URL must not point the connector at another host."""

    def _driver(self, url):
        return OdpODataDriver(
            {
                "base_url": "https://sap.example.com:44300",
                "user": "u",
                "password": "p",
                "protocol": {"mode": "odp_odata", "objects": [{"url": url}]},
            }
        )

    def test_a_relative_path_resolves_against_the_base_url(self):
        d = self._driver("/sap/opu/odata/sap/Z_SRV/FactsOfZ")
        assert d._resolve_url("/sap/opu/odata/sap/Z_SRV/FactsOfZ").startswith("https://sap.example.com:44300/")

    def test_a_matching_absolute_url_is_kept(self):
        url = "https://sap.example.com:44300/sap/opu/odata/sap/Z_SRV/FactsOfZ"
        assert self._driver(url)._resolve_url(url) == url

    @pytest.mark.parametrize(
        "hostile",
        [
            "http://169.254.169.254/latest/meta-data/",
            "https://evil.example.com/sap/opu/odata/sap/Z_SRV/FactsOfZ",
            "https://sap.example.com:8080/sap/opu/odata/sap/Z_SRV/FactsOfZ",
        ],
    )
    def test_another_host_or_port_is_refused(self, hostile):
        with pytest.raises(Exception, match="base_url"):
            self._driver(hostile)._resolve_url(hostile)


class TestConfiguredStreamsAreNotSilentlyDropped:
    def test_a_stream_that_vanished_from_sap_is_an_error_not_a_silent_success(self, caplog):
        """A renamed table or revoked authorization must not look like zero rows."""
        from unittest.mock import MagicMock

        source = SourceSap()
        configured = MagicMock()
        configured.stream.name = "GONE"
        with caplog.at_level(logging.WARNING), pytest.raises(Exception, match="GONE"):
            source._assert_all_configured_streams_found({"GONE": configured}, ["STILL_HERE"])

    def test_all_present_is_fine(self):
        source = SourceSap()
        source._assert_all_configured_streams_found({"A": object()}, ["A", "B"])


class TestWorkerClamp:
    @pytest.mark.parametrize("value,expected", [(0, 1), (-5, 1), (1, 1), (8, 8), (999, 32), ("nonsense", 4), (None, 4)])
    def test_concurrency_is_clamped_to_the_spec_range(self, value, expected):
        assert SourceSap._num_workers({"concurrency": value}) == expected
