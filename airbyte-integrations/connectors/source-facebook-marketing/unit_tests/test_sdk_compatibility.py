#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Tests verifying facebook-business SDK v25 compatibility.

These tests ensure that the connector's dynamic enum generation from SDK objects,
monkey-patching of the Cursor class, and key imports all work correctly after
bumping the facebook-business SDK from v23 to v25.
"""

import pytest
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi


# Fields that were removed from AdsInsights.Field between SDK v23 and v25.
# If any of these reappear in a future SDK version, the test should be updated.
_FIELDS_REMOVED_IN_V25 = [
    "product_brand",
    "product_category",
    "product_content_id",
    "product_custom_label_0",
    "product_custom_label_1",
    "product_custom_label_2",
    "product_custom_label_3",
    "product_custom_label_4",
    "product_group_content_id",
    "product_name",
]


def test_sdk_targets_api_v25():
    """Verify the SDK is targeting Marketing API v25.0."""
    assert FacebookAdsApi.API_VERSION == "v25.0", (
        f"Expected SDK to target API v25.0, but got {FacebookAdsApi.API_VERSION}. "
        "The facebook-business dependency may not have been bumped correctly."
    )


@pytest.mark.parametrize(
    "field_name",
    [pytest.param(f, id=f) for f in _FIELDS_REMOVED_IN_V25],
)
def test_removed_fields_not_in_sdk(field_name):
    """Verify that fields removed in v25 are no longer present in AdsInsights.Field."""
    assert not hasattr(AdsInsights.Field, field_name), f"Field '{field_name}' was expected to be removed in SDK v25 but is still present."


def test_valid_fields_enum_excludes_removed_fields():
    """Verify that the connector's ValidFields enum correctly excludes _REMOVED_FIELDS."""
    from source_facebook_marketing.spec import _REMOVED_FIELDS, ValidFields

    valid_field_names = {member.name for member in ValidFields}
    for removed in _REMOVED_FIELDS:
        assert removed not in valid_field_names, f"Removed field '{removed}' should not appear in ValidFields enum."


def test_valid_fields_enum_contains_expected_fields():
    """Verify that common AdsInsights fields are still available in ValidFields."""
    from source_facebook_marketing.spec import ValidFields

    expected_fields = ["impressions", "clicks", "spend", "reach", "account_id", "campaign_id"]
    valid_field_names = {member.name for member in ValidFields}
    for field in expected_fields:
        assert field in valid_field_names, f"Expected field '{field}' is missing from ValidFields enum."


def test_valid_breakdowns_enum_loads():
    """Verify that the ValidBreakdowns enum loads correctly from SDK v25."""
    from source_facebook_marketing.spec import ValidBreakdowns

    breakdown_names = {member.name for member in ValidBreakdowns}
    # user_segment_key is manually added in spec.py
    assert "user_segment_key" in breakdown_names, "Custom breakdown 'user_segment_key' should be present."
    # age and gender are standard breakdowns that should always be present
    assert "age" in breakdown_names, "Standard breakdown 'age' should be present."
    assert "gender" in breakdown_names, "Standard breakdown 'gender' should be present."


def test_valid_action_breakdowns_enum_loads():
    """Verify that the ValidActionBreakdowns enum loads correctly from SDK v25."""
    from source_facebook_marketing.spec import ValidActionBreakdowns

    action_breakdown_names = {member.name for member in ValidActionBreakdowns}
    assert "action_type" in action_breakdown_names, "Standard action breakdown 'action_type' should be present."


def test_status_enums_load():
    """Verify that EffectiveStatus enums for Campaign, AdSet, and Ad load correctly."""
    from source_facebook_marketing.spec import ValidAdSetStatuses, ValidAdStatuses, ValidCampaignStatuses

    # Each status enum should have members
    assert len(list(ValidCampaignStatuses)) > 0, "ValidCampaignStatuses should not be empty."
    assert len(list(ValidAdSetStatuses)) > 0, "ValidAdSetStatuses should not be empty."
    assert len(list(ValidAdStatuses)) > 0, "ValidAdStatuses should not be empty."


def test_cursor_monkey_patch_applies():
    """Verify that the CursorPatch monkey-patch still works with SDK v25."""
    # Import the connector module which applies the monkey-patch
    import source_facebook_marketing  # noqa: F401
    from facebook_business import api
    from source_facebook_marketing.streams.patches import CursorPatch

    assert api.Cursor is CursorPatch, "Monkey-patch failed: api.Cursor should be CursorPatch after importing source_facebook_marketing."


def test_key_sdk_imports():
    """Verify that all key SDK classes used by the connector are importable from v25."""
    # These imports would fail if the SDK removed or renamed any of these classes
    from facebook_business.adobjects.adaccount import AdAccount  # noqa: F401
    from facebook_business.adobjects.adcreative import AdCreative  # noqa: F401
    from facebook_business.adobjects.adimage import AdImage  # noqa: F401
    from facebook_business.adobjects.adreportrun import AdReportRun  # noqa: F401
    from facebook_business.adobjects.objectparser import ObjectParser  # noqa: F401
    from facebook_business.adobjects.user import User  # noqa: F401
    from facebook_business.api import FacebookAdsApiBatch, FacebookResponse  # noqa: F401
    from facebook_business.exceptions import FacebookRequestError  # noqa: F401
