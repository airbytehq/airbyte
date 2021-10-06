#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pytest
from source_acceptance_test.utils.compare import serialize


@pytest.fixture(name="not_sorted_data")
def not_sorted_data_fixture():
    return [
        {
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
    ]


@pytest.fixture(name="sorted_data")
def sorted_data_fixture():
    return [
        {
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
    ]


def test_compare_two_records(not_sorted_data, sorted_data):
    """Test that compare two records with equals, not sorted data."""
    output_diff = set(map(serialize, sorted_data)) - set(map(serialize, not_sorted_data))
    assert not output_diff
