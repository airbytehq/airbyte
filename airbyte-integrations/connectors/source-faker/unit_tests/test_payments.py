#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import multiprocessing.process

import jsonschema
import pytest
from source_faker import SourceFaker
from source_faker.payment_generator import CURRENCIES, METHODS, PaymentGenerator
from source_faker.purchase_generator import PurchaseGenerator
from source_faker.utils import read_json

from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer, ConfiguredAirbyteCatalog, ConfiguredAirbyteStreamSerializer, Type


class MockLogger:
    def debug(a, b, **kwargs):
        return None

    def info(a, b, **kwargs):
        return None

    def exception(a, b, **kwargs):
        print(b)
        return None

    def isEnabledFor(a, b, **kwargs):
        return False


logger = MockLogger()


@pytest.fixture(autouse=True)
def isolate_worker_identities(monkeypatch):
    # the generators seed their RNGs with seed + pool worker identity, and identities
    # come from this global counter; isolate it so we don't shift seeds in other tests
    monkeypatch.setattr(multiprocessing.process, "_process_counter", itertools.count(1))


def test_payment_generator_matches_purchase_generator():
    # in-process there is no pool worker identity, so seed_with_offset == seed
    pg = PurchaseGenerator("purchases", 100)
    pg.prepare()
    purchases = [m.record.data for uid in range(200) for m in pg.generate(uid)]

    payg = PaymentGenerator("payments", 100)
    payg.prepare()
    payments = [p for uid in range(200) for p in payg.generate(uid)]

    paid_purchases = [p for p in purchases if p["purchased_at"] is not None]
    assert len(payments) == len(paid_purchases)

    for purchase, payment in zip(paid_purchases, payments):
        assert payment["purchase_id"] == purchase["id"]
        assert payment["user_id"] == purchase["user_id"]
        assert payment["paid_at"] == purchase["purchased_at"]
        assert payment["status"] == ("refunded" if purchase["returned_at"] is not None else "captured")
        assert payment["amount"] == round(float(payg.product_prices[purchase["product_id"]]), 2)

    statuses = {p["status"] for p in payments}
    assert "refunded" in statuses
    assert "captured" in statuses


def test_payment_generator_currency_method_deterministic():
    def generate():
        payg = PaymentGenerator("payments", 100)
        payg.prepare()
        return [(p["purchase_id"], p["currency"], p["method"], p["amount"]) for uid in range(200) for p in payg.generate(uid)]

    first = generate()
    second = generate()
    assert first == second
    for _, currency, method, _ in first:
        assert currency in CURRENCIES
        assert method in METHODS


def test_read_payments():
    source = SourceFaker()
    config = {"count": 1000, "records_per_slice": 100, "parallelism": 1, "seed": 0}
    stream_dict = {
        "stream": {"name": "payments", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    catalog_message = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=source.discover(None, config)))
    payments_schema = next(s["json_schema"] for s in catalog_message["catalog"]["streams"] if s["name"] == "payments")

    estimate_row_count = 0
    state_messages = []
    records = []
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            records.append(row.record.data)
        if row.type is Type.STATE:
            state_messages.append(row)

    assert 0 < len(records) <= 1000
    assert [r["id"] for r in records] == list(range(1, len(records) + 1))
    assert len({r["purchase_id"] for r in records}) == len(records)
    for record in records:
        jsonschema.validate(record, payments_schema)
    assert estimate_row_count > 0
    # the CDK checkpoints every state_checkpoint_interval (records_per_slice) records,
    # plus a final state at the end of the stream
    assert len(state_messages) == len(records) // 100 + 1
    last_stream_state = state_messages[-1].state.stream.stream_state
    assert getattr(last_stream_state, "updated_at", None) is not None
    assert last_stream_state.loop_offset == 1000


def test_read_payments_always_updated_false_with_state():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1, "always_updated": False}
    stream_dict = {
        "stream": {"name": "payments", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)
    assert sum(1 for row in iterator if row.type is Type.RECORD) > 0

    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

    stream_descriptor = StreamDescriptor(name="payments", namespace=None)
    stream_state = AirbyteStreamState(stream_descriptor=stream_descriptor, stream_state=AirbyteStateBlob(updated_at="something"))
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]
    iterator = source.read(logger, config, catalog, state)
    assert sum(1 for row in iterator if row.type is Type.RECORD) == 0


def test_existing_streams_unchanged():
    source = SourceFaker()
    config = {"count": 1, "seed": 100, "parallelism": 1}
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=source.discover(None, config)))
    assert [s["name"] for s in catalog["catalog"]["streams"]] == ["products", "users", "purchases", "payments"]
