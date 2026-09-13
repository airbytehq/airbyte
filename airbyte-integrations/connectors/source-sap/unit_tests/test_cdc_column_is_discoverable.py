"""The tombstone column has to survive the route `discover` takes.

`build_stream` declares `_ab_cdc_deleted_at` on a delta-capable stream, but the
catalog the platform sees comes from `StreamFacade`, which asks the legacy shim
for the schema. The shim returned the raw SAP schema, so a destination reading
the catalog never learned about the column that tells it a row was deleted.
"""

from source_sap.protocols.base import SapObject
from source_sap.source import _LegacyStreamShim
from source_sap.streams import CDC_DELETED_AT

SCHEMA = {"type": "object", "properties": {"CARRID": {"type": ["null", "string"]}}}


class TestTheShimAgreesWithTheStream:
    def test_a_delta_capable_object_declares_the_tombstone(self):
        obj = SapObject(name="S", json_schema=SCHEMA, change_mode_field="ODQ_CHANGEMODE")
        assert CDC_DELETED_AT in _LegacyStreamShim(obj).get_json_schema()["properties"]

    def test_a_snapshot_object_does_not(self):
        obj = SapObject(name="S", json_schema=SCHEMA)
        assert CDC_DELETED_AT not in _LegacyStreamShim(obj).get_json_schema()["properties"]

    def test_the_sap_fields_are_still_there(self):
        obj = SapObject(name="S", json_schema=SCHEMA, change_mode_field="ODQ_CHANGEMODE")
        assert "CARRID" in _LegacyStreamShim(obj).get_json_schema()["properties"]

    def test_the_object_schema_is_not_mutated(self):
        obj = SapObject(name="S", json_schema=SCHEMA, change_mode_field="ODQ_CHANGEMODE")
        _LegacyStreamShim(obj).get_json_schema()
        assert CDC_DELETED_AT not in obj.json_schema["properties"]
