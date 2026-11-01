#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""The `groups` and `sections` of the stepped setup form, and CHECK through the CDK entrypoint with the `check-section` key."""

import json

import pytest
from source_shopify.source import SourceShopify

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.models import Status, Type


ACCOUNT_SECTION_CONFIG = {
    "check-section": "account",
    "shop": "test-shop",
    "credentials": {"auth_method": "api_password", "api_password": "api_password"},
}

FULL_CONFIG = {
    "shop": "test-shop",
    "credentials": {"auth_method": "api_password", "api_password": "api_password"},
    "start_date": "2020-11-01",
    "bulk_window_in_days": 7,
    "job_checkpoint_interval": 50000,
    "job_termination_threshold": 3600,
    "lookback_window_in_days": 2,
}


@pytest.fixture(name="schema")
def schema_fixture():
    return SourceShopify().spec(None).connectionSpecification


def test_spec_declares_groups_and_sections(schema):
    """The stepped setup form: two sections, "Connect account" (checked) and "Review & set up" (covered by the full check)."""
    assert [group["id"] for group in schema["groups"]] == ["account", "filters", "advanced"]
    assert schema["sections"] == [
        {
            "id": "account",
            "title": "Connect account",
            "order": 0,
            "description": "Install the Airbyte app on the Shopify store you want to sync.",
            "groups": ["account", "filters"],
            "check": True,
        },
        {
            "id": "review",
            "title": "Review & set up",
            "order": 1,
            "description": "Name your source and check the optional settings.",
            "groups": ["advanced"],
        },
    ]
    # Every section group is declared, and every property belongs to a group of some section.
    declared_groups = {group["id"] for group in schema["groups"]}
    section_groups = {group for section in schema["sections"] for group in section["groups"]}
    assert section_groups <= declared_groups
    assert {name: prop["group"] for name, prop in schema["properties"].items()} == {
        "credentials": "account",
        "shop": "account",
        "start_date": "filters",
        "fetch_transactions_user_id": "filters",
        "fulfillment_orders_include_closed": "filters",
        "job_product_variants_include_pres_prices": "filters",
        "populate_top_level_orders_customer_fields": "filters",
        "bulk_window_in_days": "advanced",
        "job_checkpoint_interval": "advanced",
        "job_termination_threshold": "advanced",
        "lookback_window_in_days": "advanced",
    }
    # The required fields all belong to the first section, so its check can validate them.
    assert {schema["properties"][name]["group"] for name in schema["required"]} == {"account"}


def test_spec_orders_properties_as_the_form_shows_them(schema):
    orders = {name: prop["order"] for name, prop in schema["properties"].items()}
    assert sorted(orders, key=orders.get) == [
        "credentials",
        "shop",
        "start_date",
        "fetch_transactions_user_id",
        "fulfillment_orders_include_closed",
        "job_product_variants_include_pres_prices",
        "populate_top_level_orders_customer_fields",
        "bulk_window_in_days",
        "job_checkpoint_interval",
        "job_termination_threshold",
        "lookback_window_in_days",
    ]
    assert len(set(orders.values())) == len(orders)


def _run_check(tmp_path, config):
    """Runs `check` end to end through the CDK entrypoint and returns the (status, message) of the CONNECTION_STATUS message."""
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    entrypoint = AirbyteEntrypoint(SourceShopify())
    messages = [json.loads(line) for line in entrypoint.run(entrypoint.parse_args(["check", "--config", str(config_path)]))]
    statuses = [message["connectionStatus"] for message in messages if message["type"] == Type.CONNECTION_STATUS.value]
    assert len(statuses) == 1, messages
    return statuses[0]["status"], statuses[0].get("message")


@pytest.fixture(name="shop_read")
def shop_read_fixture(mocker):
    return mocker.patch("source_shopify.streams.streams.Shop.read_records", return_value=[{"id": 1}])


def test_check_of_the_account_section_reads_the_shop_and_succeeds(tmp_path, shop_read):
    assert _run_check(tmp_path, ACCOUNT_SECTION_CONFIG) == (Status.SUCCEEDED.value, None)
    shop_read.assert_called_once()


def test_check_of_the_account_section_fails_on_an_unknown_shop(tmp_path, mocker):
    mocker.patch("source_shopify.streams.streams.Shop.read_records", return_value=[])

    status, message = _run_check(tmp_path, ACCOUNT_SECTION_CONFIG)

    assert status == Status.FAILED.value
    assert "Failed to access the Shopify store `test-shop`" in message


def test_check_of_the_account_section_requires_its_fields(tmp_path, shop_read):
    config = {key: value for key, value in ACCOUNT_SECTION_CONFIG.items() if key != "shop"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'shop' is a required property")
    shop_read.assert_not_called()


def test_check_of_the_account_section_still_validates_the_present_fields(tmp_path, shop_read):
    config = {**ACCOUNT_SECTION_CONFIG, "start_date": "not-a-date"}

    status, message = _run_check(tmp_path, config)

    assert status == Status.FAILED.value
    assert message.startswith("Config validation error: ")
    shop_read.assert_not_called()


def test_check_of_an_unknown_section_fails(tmp_path, shop_read):
    assert _run_check(tmp_path, {**ACCOUNT_SECTION_CONFIG, "check-section": "nope"}) == (
        Status.FAILED.value,
        "Unknown check-section 'nope'; the connector specification declares: account, review.",
    )
    shop_read.assert_not_called()


def test_check_of_the_review_section_is_rejected_as_it_has_no_check(tmp_path, shop_read):
    assert _run_check(tmp_path, {**FULL_CONFIG, "check-section": "review"}) == (
        Status.FAILED.value,
        "Section 'review' has no check: the connector specification does not declare \"check\": true for it.",
    )
    shop_read.assert_not_called()


def test_check_without_the_key_validates_the_full_spec(tmp_path, shop_read):
    config = {key: value for key, value in FULL_CONFIG.items() if key != "shop"}

    assert _run_check(tmp_path, config) == (Status.FAILED.value, "Config validation error: 'shop' is a required property")
    shop_read.assert_not_called()


def test_check_without_the_key_succeeds_with_the_full_config(tmp_path, shop_read):
    assert _run_check(tmp_path, FULL_CONFIG) == (Status.SUCCEEDED.value, None)
    shop_read.assert_called_once()
