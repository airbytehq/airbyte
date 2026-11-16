#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any

import pytest
from requests_mock import Mocker
from source_shopify.source import SourceShopify
from source_shopify.streams.streams import Orders

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources.utils.slice_logger import DebugSliceLogger


@pytest.fixture
def customer_field_names(auth_config: dict[str, Any]) -> set[str]:
    schema = Orders(auth_config).get_json_schema()
    return {f"customer_{field}" for field in schema["properties"]["customer"]["properties"]}


@pytest.mark.parametrize("input_shape", ["list", "dict", "generator"])
def test_produce_records_populates_customer_fields_when_enabled(auth_config: dict[str, Any], input_shape: str) -> None:
    stream = Orders(auth_config | {"populate_top_level_orders_customer_fields": True})
    customer = {
        "id": 7,
        "email": "test@example.invalid",
        "total_spent": "1.50",
        "default_address": {"city": "Fair Lawn", "zip": "07410"},
    }
    record = {"id": 1, "updated_at": "2026-09-28T00:00:00Z", "customer": customer}
    records = record if input_shape == "dict" else [record]
    if input_shape == "generator":
        records = iter(records)
    output = list(stream.produce_records(records))[0]

    assert output["customer_id"] == 7
    assert output["customer_email"] == "test@example.invalid"
    assert output["customer_total_spent"] == 1.5
    assert output["customer_default_address"] == {"city": "Fair Lawn", "zip": "07410"}
    assert output["customer_phone"] is None
    assert output["customer"] == customer | {"total_spent": 1.5}
    assert output["id"] == 1
    assert output["updated_at"] == "2026-09-28T00:00:00Z"
    assert output["shop_url"] == auth_config["shop"]


@pytest.mark.parametrize("toggle_config", [{}, {"populate_top_level_orders_customer_fields": False}], ids=["omitted", "disabled"])
@pytest.mark.parametrize("input_shape", ["list", "dict", "generator"])
def test_produce_records_defaults_customer_fields_to_null(
    auth_config: dict[str, Any], customer_field_names: set[str], toggle_config: dict[str, bool], input_shape: str
) -> None:
    stream = Orders(auth_config | toggle_config)
    customer = {"id": 7, "email": "test@example.invalid", "default_address": {"city": "Fair Lawn"}}
    record = {"id": 1, "customer": customer}
    records = record if input_shape == "dict" else [record]
    if input_shape == "generator":
        records = iter(records)
    output = list(stream.produce_records(records))[0]

    assert {field: output[field] for field in customer_field_names} == dict.fromkeys(customer_field_names)
    assert output["customer"] == customer
    assert output["id"] == 1
    assert output["shop_url"] == auth_config["shop"]


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("customer_record", [{}, {"customer": None}, {"customer": {}}], ids=["missing", "null", "empty"])
def test_produce_records_unavailable_customer_fields_are_null(
    auth_config: dict[str, Any], customer_field_names: set[str], enabled: bool, customer_record: dict[str, Any]
) -> None:
    stream = Orders(auth_config | {"populate_top_level_orders_customer_fields": enabled})
    output = list(stream.produce_records([{"id": 1} | customer_record]))[0]

    assert {field: output[field] for field in customer_field_names} == dict.fromkeys(customer_field_names)
    assert ("customer" in output) == ("customer" in customer_record)
    assert output.get("customer") == customer_record.get("customer")


@pytest.mark.parametrize("enabled", [False, True])
def test_customer_population_preserves_native_fields_and_ignores_unknown_attributes(auth_config: dict[str, Any], enabled: bool) -> None:
    stream = Orders(auth_config | {"populate_top_level_orders_customer_fields": enabled})
    customer = {"id": 7, "locale": "fr", "unexpected": "value"}
    output = list(stream.produce_records([{"id": 1, "customer_locale": "en", "customer": customer}]))[0]

    assert output["customer_locale"] == "en"
    assert "customer_unexpected" not in output
    assert output["customer"] == customer


def test_orders_schema_is_identical_for_all_toggle_settings(auth_config: dict[str, Any]) -> None:
    default_schema = Orders(auth_config).get_json_schema()

    assert Orders(auth_config | {"populate_top_level_orders_customer_fields": False}).get_json_schema() == default_schema
    assert Orders(auth_config | {"populate_top_level_orders_customer_fields": True}).get_json_schema() == default_schema


def test_orders_schema_has_flattened_customer_fields() -> None:
    schema = Orders(config={"authenticator": None, "shop": "test"}).get_json_schema()
    customer_properties = schema["properties"]["customer"]["properties"]
    for key, field_schema in customer_properties.items():
        flattened = schema["properties"][f"customer_{key}"]
        assert "null" in flattened["type"]
        if key == "accepts_marketing_updated_at":
            # the nested field is exempt from the date-time annotation because typed destinations
            # store `customer` as a single JSON column; the flattened column is annotated
            assert flattened == field_schema | {"format": "date-time"}
        else:
            assert flattened == field_schema


def test_customer_population_config_is_optional_and_defaults_to_false(logger: logging.Logger) -> None:
    spec = SourceShopify().spec(logger).connectionSpecification
    field = spec["properties"]["populate_top_level_orders_customer_fields"]

    assert field["type"] == "boolean"
    assert field["default"] is False
    assert "populate_top_level_orders_customer_fields" not in spec.get("required", [])


@pytest.mark.parametrize("enabled", [None, False, True], ids=["omitted", "disabled", "enabled"])
@pytest.mark.parametrize("selection", ["all", "customer_email", "customer", "customer_locale", "id"])
def test_read_warns_once_only_for_selected_redacted_customer_fields(
    auth_config: dict[str, Any], requests_mock: Mocker, caplog: pytest.LogCaptureFixture, enabled: bool | None, selection: str
) -> None:
    config = auth_config if enabled is None else auth_config | {"populate_top_level_orders_customer_fields": enabled}
    stream = Orders(config)
    schema = stream.get_json_schema()
    if selection != "all":
        schema = {**schema, "properties": {field: schema["properties"][field] for field in {"id", "updated_at", selection}}}
    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="orders", json_schema=schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )
    customer = {"id": 7, "email": "test@example.invalid"}
    requests_mock.get(
        f"{stream.url_base}orders.json",
        [
            {
                "json": {"orders": [{"id": 1, "updated_at": "2026-09-29T00:00:00Z", "customer": customer}]},
                "headers": {"Link": f'<{stream.url_base}orders.json?page_info=second>; rel="next"'},
            },
            {"json": {"orders": [{"id": 2, "updated_at": "2026-09-29T00:00:00Z", "customer": customer}]}},
        ],
    )
    requests_mock.get(f"{stream.url_base}events.json", json={"events": []})

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        records = list(stream.read(configured_stream, logging.getLogger("airbyte"), DebugSliceLogger(), {}, None, InternalConfig()))

    assert [record["id"] for record in records if isinstance(record, dict)] == [1, 2]
    warnings = [record for record in caplog.records if "redacted to null" in record.getMessage()]
    should_warn = not enabled and selection in {"all", "customer_email"}
    assert len(warnings) == int(should_warn)
    if should_warn:
        assert warnings[0].levelno == logging.WARNING
        assert '"Populate top-level customer fields in Orders" is off.' in warnings[0].getMessage()
        assert "The nested customer object is not redacted." in warnings[0].getMessage()
        assert "test@example.invalid" not in warnings[0].getMessage()


def test_internal_order_reads_without_a_configured_catalog_do_not_warn(
    auth_config: dict[str, Any], caplog: pytest.LogCaptureFixture
) -> None:
    stream = Orders(auth_config)

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        list(stream.produce_records([{"id": 1, "customer": {"id": 7}}]))

    assert not caplog.records


def test_empty_order_results_do_not_warn(auth_config: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    stream = Orders(auth_config)
    stream.configured_json_schema = stream.get_json_schema()

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        assert list(stream.produce_records([])) == []

    assert not caplog.records
