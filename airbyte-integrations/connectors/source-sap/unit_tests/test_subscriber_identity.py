"""ODP subscriber-process identity.

The subscriber process is the ODQ subscription key on the SAP side. Two Airbyte
connections that resolve to the same name share one subscription and consume each
other's deltas -- each seeing a partial change set, permanently. Nothing in the
Airbyte protocol hands the connector a connection id, so the name must be derived
from something that actually differs between connections.
"""

import pytest

from source_sap.protocols.odp_rfc import OdpRfcDriver, subscriber_process_for


def _config(**over):
    base = {"ashost": "sap1.example.com", "sysnr": "00", "client": "100", "user": "u", "password": "p"}
    base.update(over)
    return base


class TestDerivation:
    def test_is_stable_for_the_same_inputs(self):
        a = subscriber_process_for(_config(), "ABAP_CDS", "ZV$F")
        assert a == subscriber_process_for(_config(), "ABAP_CDS", "ZV$F")

    def test_differs_per_object(self):
        assert subscriber_process_for(_config(), "ABAP_CDS", "A$F") != subscriber_process_for(
            _config(), "ABAP_CDS", "B$F"
        )

    def test_differs_per_context(self):
        assert subscriber_process_for(_config(), "BW", "X$F") != subscriber_process_for(_config(), "ABAP_CDS", "X$F")

    def test_differs_per_sap_client(self):
        assert subscriber_process_for(_config(client="100"), "BW", "X") != subscriber_process_for(
            _config(client="200"), "BW", "X"
        )

    def test_differs_per_sap_user(self):
        # Two connections against one system usually differ by the service user.
        assert subscriber_process_for(_config(user="a"), "BW", "X") != subscriber_process_for(
            _config(user="b"), "BW", "X"
        )

    def test_fits_the_sap_char32_field(self):
        got = subscriber_process_for(_config(), "ABAP_CDS", "SOME$VERY$LONG$ODP$NAME$HERE$F")
        assert len(got) <= 32

    def test_is_upper_case_and_sap_safe(self):
        got = subscriber_process_for(_config(user="u/x"), "ABAP_CDS", "ZV$F")
        assert got == got.upper()
        assert all(c.isalnum() or c == "_" for c in got)


class TestCollisionWarning:
    def _driver(self, **protocol):
        return OdpRfcDriver({**_config(), "protocol": {"mode": "odp_rfc", **protocol}})

    def test_a_derived_name_is_flagged_as_shared_risk(self, caplog):
        """Two Airbyte connections with identical config still collide.

        The protocol gives the connector no connection id, so the honest thing is
        to say so rather than imply per-connection uniqueness.
        """
        import logging

        with caplog.at_level(logging.WARNING):
            self._driver(context="BW", objects=[{"name": "X"}]).warn_if_subscriber_derived("X")
        assert "subscriber_process" in caplog.text

    def test_an_explicit_name_is_not_flagged(self, caplog):
        import logging

        with caplog.at_level(logging.WARNING):
            self._driver(
                context="BW", objects=[{"name": "X", "subscriber_process": "MY_PIPELINE"}]
            ).warn_if_subscriber_derived("X")
        assert caplog.text == ""


class TestValidation:
    def _driver(self, **protocol):
        return OdpRfcDriver({**_config(), "protocol": {"mode": "odp_rfc", **protocol}})

    @pytest.mark.parametrize("bad", ["has space", "lower", "toolong" * 6, "semi;colon"])
    def test_an_unusable_explicit_name_is_rejected(self, bad):
        with pytest.raises(Exception, match="subscriber_process"):
            self._driver(context="BW", objects=[{"name": "X", "subscriber_process": bad}])._subscriber_for(
                "BW", "X", {"subscriber_process": bad}
            )

    def test_a_blank_name_falls_back_to_derivation(self):
        # Blank means "not set" everywhere else in the config; the alternative
        # would be failing a connection over an empty optional field.
        d = self._driver(context="BW", objects=[{"name": "X", "subscriber_process": "  "}])
        assert d._subscriber_for("BW", "X", {"subscriber_process": "  "}).startswith("AB_")

    def test_a_valid_name_is_accepted(self):
        d = self._driver(context="BW", objects=[{"name": "X", "subscriber_process": "AB_NIGHTLY_1"}])
        assert d._subscriber_for("BW", "X", {"subscriber_process": "AB_NIGHTLY_1"}) == "AB_NIGHTLY_1"
