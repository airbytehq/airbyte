"""A configured primary key must beat the one SAP reports.

The spec offers `primary_key` on every object list. For RFC and ODP the driver
derived the key from SAP's own field metadata and ignored the configured value
outright — so the form accepted a setting that did nothing, which is worse than
not offering it.

SAP's key is right most of the time. It is wrong when a CDS view or ODP provider
reports no key at all, or reports one that is not unique in the extract.
"""

from unittest.mock import MagicMock

import pytest

CONN = {"ashost": "h", "sysnr": "00", "client": "001", "user": "u", "password": "p"}

FIELDS = [
    ("0001", "X", "MANDT", "Client", "CLNT", "3", "0"),
    ("0002", "X", "CARRID", "Airline", "CHAR", "3", "0"),
    ("0003", "", "PRICE", "Fare", "CURR", "15", "2"),
]


def _session(rows):
    session = MagicMock()
    session.cursor.return_value.execute.return_value.fetchall.return_value = rows
    return session


class TestRfcPrimaryKeyOverride:
    def _discover(self, objects):
        from source_sap.protocols.rfc import RfcDriver

        driver = RfcDriver({**CONN, "protocol": {"mode": "rfc", "objects": objects}})
        session = MagicMock()
        # Objects are named explicitly, so no table pattern is queried; the only
        # call is sap_describe_fields.
        session.cursor.return_value.execute.return_value.fetchall.return_value = FIELDS
        return driver.discover(session)

    def test_sap_key_is_used_when_nothing_is_configured(self):
        (obj,) = self._discover([{"name": "T"}])
        assert obj.primary_key == [["MANDT"], ["CARRID"]]

    def test_a_configured_key_wins(self):
        (obj,) = self._discover([{"name": "T", "primary_key": ["CARRID"]}])
        assert obj.primary_key == [["CARRID"]]

    def test_a_configured_composite_key_wins(self):
        (obj,) = self._discover([{"name": "T", "primary_key": ["CARRID", "PRICE"]}])
        assert obj.primary_key == [["CARRID"], ["PRICE"]]


class TestOdpPrimaryKeyOverride:
    def _discover(self, objects):
        from source_sap.protocols.odp_rfc import OdpRfcDriver

        driver = OdpRfcDriver({**CONN, "protocol": {"mode": "odp_rfc", "context": "BW", "objects": objects}})
        session = MagicMock()
        session.cursor.return_value.execute.return_value.fetchone.return_value = (
            True,
            True,
            [
                {"technical_name": "ID", "abap_type": "CHAR", "length": 10, "decimals": 0, "key": True},
                {"technical_name": "NAME", "abap_type": "CHAR", "length": 40, "decimals": 0, "key": False},
            ],
        )
        return driver.discover(session)

    def test_sap_key_is_used_when_nothing_is_configured(self):
        (obj,) = self._discover([{"name": "N"}])
        assert obj.primary_key == [["ID"]]

    def test_a_configured_key_wins(self):
        (obj,) = self._discover([{"name": "N", "primary_key": ["NAME"]}])
        assert obj.primary_key == [["NAME"]]


class TestSpecAndDriversAgree:
    @pytest.mark.parametrize("mode", ["rfc", "rfc_invoke", "bics", "odp_rfc", "odp_odata"])
    def test_every_field_the_spec_offers_is_read_by_its_driver(self, mode):
        """The spec must not advertise a setting the driver ignores."""
        import ast
        import pathlib

        import yaml

        spec = yaml.safe_load(pathlib.Path("source_sap/spec.yaml").read_text())
        branch = next(
            b
            for b in spec["connectionSpecification"]["properties"]["protocol"]["oneOf"]
            if b["properties"]["mode"]["const"] == mode
        )
        offered = set((branch["properties"].get("objects") or {}).get("items", {}).get("properties", {}))
        module = ast.parse(
            pathlib.Path(f"source_sap/protocols/{'rfc_invoke' if mode == 'rfc_invoke' else mode}.py").read_text()
        )
        # Where config is actually read: a `.get("field")` call, or the name in a
        # tuple literal, which is how rfc.py drives THREADS and MAX_ROWS from a
        # table. A bare mention does not count -- BICS `properties` satisfied the
        # old substring check through `schema["properties"]` elsewhere in the
        # file, and would have stayed green with the override read deleted.
        read: set[str] = set()
        for node in ast.walk(module):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        read.add(arg.value)
            elif isinstance(node, ast.Tuple):
                for element in node.elts:
                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                        read.add(element.value)
        # `name` addresses the object rather than configuring it.
        ignored = sorted(offered - {"name"} - read)
        assert not ignored, f"{mode}: the spec offers fields the driver never reads: {ignored}"
