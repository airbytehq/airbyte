#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from functools import partial

import pytest
from source_acceptance_test.utils.compare import make_hashable


def not_sorted_data():
    return {
        "date_created": "0001-01-01T00:00:00",
        "date_updated": "0001-01-01T00:00:00",
        "editable": False,
        "id": "superuser",
        "name": "Super User",
        "organization_id": "orga_ya3w9oMjeLtWe7zFGZr63Dz8ruBbjybG0EIUdUXaESi",
        "permissions": [
            "bulk_edit",
            "delete_own_opportunities",
            "export",
            "manage_group_numbers",
            "manage_email_sequences",
            "delete_leads",
            "call_coach_listen",
            "call_coach_barge",
            "manage_others_tasks",
            "manage_others_activities",
            "delete_own_tasks",
            "manage_customizations",
            "manage_team_smart_views",
            "bulk_delete",
            "manage_team_email_templates",
            "bulk_email",
            "merge_leads",
            "calling",
            "bulk_sequence_subscriptions",
            "bulk_import",
            "delete_own_activities",
            "manage_others_opportunities",
        ],
    }


def sorted_data():
    return {
        "date_created": "0001-01-01T00:00:00",
        "date_updated": "0001-01-01T00:00:00",
        "editable": False,
        "id": "superuser",
        "name": "Super User",
        "organization_id": "orga_ya3w9oMjeLtWe7zFGZr63Dz8ruBbjybG0EIUdUXaESi",
        "permissions": [
            "bulk_delete",
            "bulk_edit",
            "bulk_email",
            "bulk_import",
            "bulk_sequence_subscriptions",
            "call_coach_barge",
            "call_coach_listen",
            "calling",
            "delete_leads",
            "delete_own_activities",
            "delete_own_opportunities",
            "delete_own_tasks",
            "export",
            "manage_customizations",
            "manage_email_sequences",
            "manage_group_numbers",
            "manage_others_activities",
            "manage_others_opportunities",
            "manage_others_tasks",
            "manage_team_email_templates",
            "manage_team_smart_views",
            "merge_leads",
        ],
    }


@pytest.mark.parametrize(
    "obj1,obj2,is_same",
    [
        (sorted_data(), not_sorted_data(), True),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-page",
                        "issue-percent-filters",
                    ]
                }
            },
            True,
        ),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-pag",
                        "issue-percent-filters",
                    ]
                }
            },
            False,
        ),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-page",
                    ]
                }
            },
            False,
        ),
        ({"a": 1, "b": 2}, {"b": 2, "a": 1}, True),
        ({"a": 1, "b": 2, "c": {"d": [1, 2]}}, {"b": 2, "a": 1, "c": {"d": [2, 1]}}, True),
        ({"a": 1, "b": 2, "c": {"d": [1, 2]}}, {"b": 2, "a": 1, "c": {"d": [3, 4]}}, False),
    ],
)
def test_compare_two_records_nested_with_different_orders(obj1, obj2, is_same):
    """Test that compare two records with equals, not sorted data."""
    output_diff = set(map(make_hashable, [obj1])).symmetric_difference(set(map(make_hashable, [obj2])))
    if is_same:
        assert not output_diff, f"{obj1} should be equal to {obj2}"
    else:
        assert output_diff, f"{obj1} shouldnt be equal to {obj2}"


def test_exclude_fields():
    """Test that check ignoring fields"""
    data = [
        sorted_data(),
    ]
    ignored_fields = [
        "organization_id",
    ]
    serializer = partial(make_hashable, exclude_fields=ignored_fields)
    output = map(serializer, data)
    for item in output:
        assert "organization_id" not in item
