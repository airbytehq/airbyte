"""ODP change markers -> Airbyte CDC tombstones."""

from source_sap.streams import CDC_DELETED_AT, ErplPartition


def apply(marker):
    partition = ErplPartition("s", session=None, plan=None, change_mode_field="ODQ_CHANGEMODE", driver=None)
    data = {"ID": "1", "ODQ_CHANGEMODE": marker}
    partition._apply_change_mode(data)
    return data


def test_delete_marker_becomes_a_tombstone():
    assert apply("D")[CDC_DELETED_AT] is not None


def test_lowercase_delete_marker_is_honoured():
    assert apply("d")[CDC_DELETED_AT] is not None


def test_update_after_image_is_not_a_delete():
    assert apply("U")[CDC_DELETED_AT] is None


def test_create_marker_is_not_a_delete():
    assert apply("C")[CDC_DELETED_AT] is None


def test_deltainit_rows_carry_no_marker_at_all():
    # SAP leaves ODQ_CHANGEMODE NULL on the initial load rather than setting 'C',
    # so anything that is not an explicit 'D' has to count as an upsert.
    assert apply(None)[CDC_DELETED_AT] is None


def test_empty_marker_is_not_a_delete():
    assert apply("")[CDC_DELETED_AT] is None


def test_tombstone_is_an_iso_utc_timestamp():
    value = apply("D")[CDC_DELETED_AT]
    assert value.endswith("+00:00") and value[4] == "-"


def test_nulls_are_dropped_by_the_protocol_serializer():
    """Documents why a non-deleted row has no `_ab_cdc_deleted_at` key on the wire.

    The CDK serializes records with omit_none, so null values disappear from the
    record entirely. Destinations read an absent key as null, which is what makes
    "tombstone present" the right test for a delete.
    """
    import orjson
    from airbyte_cdk.models import (
        AirbyteMessage,
        AirbyteMessageSerializer,
        AirbyteRecordMessage,
        Type,
    )

    message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream="s", data={"a": 1, "b": None}, emitted_at=1),
    )
    assert orjson.loads(orjson.dumps(AirbyteMessageSerializer.dump(message)))["record"]["data"] == {"a": 1}
