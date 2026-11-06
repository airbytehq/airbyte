#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""The `groups` and `sections` of the stepped setup form declared in the manifest spec."""

from .conftest import get_source


def _connection_specification() -> dict:
    return get_source(config={}).spec(logger=None).connectionSpecification


def test_spec_declares_groups_and_sections():
    """The stepped setup form: two sections, "Connect account" (checked) and "Review & set up" (covered by the full check)."""
    schema = _connection_specification()

    assert [group["id"] for group in schema["groups"]] == ["account", "filters", "advanced"]
    assert schema["sections"] == [
        {
            "id": "account",
            "title": "Connect account",
            "order": 0,
            "description": "Sign in to LinkedIn and choose where to start syncing from.",
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
        "start_date": "account",
        "account_ids": "filters",
        "ad_analytics_reports": "filters",
        "ad_statistics_reports": "filters",
        "lookback_window": "advanced",
        "num_workers": "advanced",
    }
    # The required fields all belong to the first section, so its check can validate them.
    assert {schema["properties"][name]["group"] for name in schema["required"]} == {"account"}


def test_spec_orders_properties_as_the_form_shows_them():
    properties = _connection_specification()["properties"]

    orders = {name: prop["order"] for name, prop in properties.items()}
    assert sorted(orders, key=orders.get) == [
        "credentials",
        "start_date",
        "account_ids",
        "ad_analytics_reports",
        "ad_statistics_reports",
        "lookback_window",
        "num_workers",
    ]
    assert len(set(orders.values())) == len(orders)
    assert properties["credentials"]["display_type"] == "radio"
