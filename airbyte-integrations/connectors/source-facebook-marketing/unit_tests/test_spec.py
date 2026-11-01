#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_facebook_marketing import SourceFacebookMarketing
from source_facebook_marketing.spec import SECTIONS


@pytest.fixture
def spec_properties():
    spec = SourceFacebookMarketing().spec(None)
    return spec.connectionSpecification["properties"]


def _access_token_descriptions(properties):
    descriptions = [properties["access_token"]["description"]]
    for option in properties["credentials"]["oneOf"]:
        descriptions.append(option["properties"]["access_token"]["description"])
    return descriptions


def test_access_token_descriptions_recommend_system_user_token(spec_properties):
    for description in _access_token_descriptions(spec_properties):
        assert "read_insights" not in description
        assert '"Marketing API" then "Tools"' not in description
        assert "System users" in description
        assert "ads_read" in description
        assert "ads_management" in description


def test_start_date_description_mentions_37_months(spec_properties):
    description = spec_properties["start_date"]["description"]
    assert "37 months" in description
    assert "2 years" not in description


def test_spec_declares_groups_and_sections():
    """The stepped setup form: two sections, "Connect account" (checked) and "Review & set up" (covered by the full check)."""
    schema = SourceFacebookMarketing().spec(None).connectionSpecification

    assert [group["id"] for group in schema["groups"]] == ["account", "filters", "advanced"]
    assert schema["sections"] == SECTIONS
    assert [section["id"] for section in schema["sections"]] == ["account", "review"]
    assert [section["order"] for section in schema["sections"]] == [0, 1]
    assert [section.get("check") for section in schema["sections"]] == [True, None]
    # Every section group is declared, and every visible property belongs to a group of some section.
    declared_groups = {group["id"] for group in schema["groups"]}
    section_groups = {group for section in schema["sections"] for group in section["groups"]}
    assert section_groups <= declared_groups
    grouped = {name: prop["group"] for name, prop in schema["properties"].items() if "group" in prop}
    assert grouped == {
        "account_ids": "account",
        "credentials": "account",
        "start_date": "filters",
        "end_date": "filters",
        "campaign_statuses": "filters",
        "adset_statuses": "filters",
        "ad_statuses": "filters",
        "custom_insights": "filters",
        "fetch_thumbnail_images": "filters",
        "default_ads_insights_action_breakdowns": "filters",
        "include_incrementality": "filters",
        "include_engaged_view": "filters",
        "insights_lookback_window": "advanced",
        "page_size": "advanced",
        "insights_job_timeout": "advanced",
    }
    assert set(grouped.values()) <= section_groups
    # The hidden properties keep no group.
    assert {name for name, prop in schema["properties"].items() if "group" not in prop} == {
        "access_token",
        "action_breakdowns_allow_empty",
        "client_id",
        "client_secret",
    }
    # The required fields all belong to the first section, so its check can validate them.
    assert {grouped[name] for name in schema["required"]} == {"account"}


def test_spec_orders_properties_as_the_form_shows_them(spec_properties):
    orders = {name: prop["order"] for name, prop in spec_properties.items() if "order" in prop}
    assert sorted(orders, key=orders.get) == [
        "account_ids",
        "credentials",
        "start_date",
        "end_date",
        "campaign_statuses",
        "adset_statuses",
        "ad_statuses",
        "custom_insights",
        "fetch_thumbnail_images",
        "default_ads_insights_action_breakdowns",
        "include_incrementality",
        "include_engaged_view",
        "insights_lookback_window",
        "page_size",
        "insights_job_timeout",
    ]
    assert len(set(orders.values())) == len(orders)
    assert spec_properties["credentials"]["display_type"] == "radio"
