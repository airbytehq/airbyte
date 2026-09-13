"""A Gateway's catalog is input, not authority.

Configured entity-set URLs go through `_resolve_url`, which refuses any host but
the configured Gateway -- the connector holds Gateway-scoped credentials and sits
inside the customer's network. URLs discovered through `service_pattern` went
straight into the read, so a Gateway that returned
`http://169.254.169.254/latest/meta-data/` in its catalog -- a compromised one,
or a MITM on a plain-http base_url, which the connector only warns about -- got
that URL fetched.
"""

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from source_sap.protocols.odp_odata import OdpODataDriver

CONN = {
    "ashost": "h",
    "sysnr": "00",
    "client": "001",
    "user": "u",
    "password": "p",
    "base_url": "https://gw.example.com:44300",
}


def _driver(**protocol):
    return OdpODataDriver({**CONN, "protocol": {"mode": "odp_odata", "service_pattern": "*", **protocol}})


def _session_returning(*urls):
    session = MagicMock()
    connection = session.disposable.return_value
    connection.execute.return_value.fetchall.return_value = [(u, f"ES{i}", "X") for i, u in enumerate(urls)]
    return session


class TestACatalogUrlOffTheGateway:
    def test_is_not_selected(self):
        session = _session_returning("http://169.254.169.254/latest/meta-data/")
        # Nothing survives the confinement, so the configuration selects nothing
        # -- which the driver reports rather than syncing an empty catalogue.
        with pytest.raises(AirbyteTracedException) as caught:
            _driver()._selected_entity_sets(session)
        assert "No ODP OData entity sets selected" in str(caught.value)

    def test_is_reported_rather_than_dropped_in_silence(self, caplog):
        session = _session_returning("http://169.254.169.254/latest/meta-data/")
        with pytest.raises(AirbyteTracedException):
            _driver()._selected_entity_sets(session)
        assert "169.254.169.254" in caplog.text

    def test_does_not_take_its_neighbours_with_it(self):
        session = _session_returning(
            "http://169.254.169.254/latest/meta-data/",
            "https://gw.example.com:44300/sap/opu/odata/sap/SRV/FactsOfX",
        )
        selected = _driver()._selected_entity_sets(session)
        assert [url for url, _ in selected] == ["https://gw.example.com:44300/sap/opu/odata/sap/SRV/FactsOfX"]


class TestACatalogUrlOnTheGateway:
    def test_is_selected(self):
        url = "https://gw.example.com:44300/sap/opu/odata/sap/SRV/FactsOfX"
        assert [u for u, _ in _driver()._selected_entity_sets(_session_returning(url))] == [url]

    def test_a_relative_catalog_url_is_resolved_against_the_base(self):
        selected = _driver()._selected_entity_sets(_session_returning("/sap/opu/odata/sap/SRV/FactsOfX"))
        assert selected[0][0] == "https://gw.example.com:44300/sap/opu/odata/sap/SRV/FactsOfX"


class TestAConfiguredUrlIsStillConfined:
    def test_an_off_gateway_configured_url_is_a_config_error(self):
        driver = _driver(objects=[{"entity_set": "E", "url": "https://elsewhere.example.net/x"}])
        with pytest.raises(AirbyteTracedException) as caught:
            driver._selected_entity_sets(_session_returning())
        assert "elsewhere.example.net" in str(caught.value)
