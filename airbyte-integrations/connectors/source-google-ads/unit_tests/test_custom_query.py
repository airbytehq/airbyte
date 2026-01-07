#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, Mock

import pytest
from source_google_ads.custom_query_stream import CustomQueryMixin, IncrementalCustomQuery
from source_google_ads.models import CustomerModel
from source_google_ads.utils import GAQL


def test_custom_query():
    input_q = """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros,
     ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type,
     ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status,
     campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id,
     campaign.app_campaign_setting.app_store FROM search_term_view"""
    output_q = IncrementalCustomQuery.insert_segments_date_expr(GAQL.parse(input_q), "1980-01-01", "1980-01-01")
    assert (
        str(output_q)
        == """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros, ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type, ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status, campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id, campaign.app_campaign_setting.app_store, segments.date FROM search_term_view WHERE segments.date BETWEEN '1980-01-01' AND '1980-01-01'"""
    )


class Obj:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def test_get_json_schema():
    query_object = MagicMock(
        return_value={
            "a": Obj(data_type=Obj(name="ENUM"), is_repeated=False, enum_values=["a", "aa"]),
            "b": Obj(data_type=Obj(name="ENUM"), is_repeated=True, enum_values=["b", "bb"]),
            "c": Obj(data_type=Obj(name="MESSAGE"), is_repeated=False),
            "d": Obj(data_type=Obj(name="MESSAGE"), is_repeated=True),
            "e": Obj(data_type=Obj(name="STRING"), is_repeated=False),
            "f": Obj(data_type=Obj(name="DATE"), is_repeated=False),
            "segments.month": Obj(data_type=Obj(name="DATE"), is_repeated=False),
        }
    )
    instance = CustomQueryMixin(config={"query": Obj(fields=["a", "b", "c", "d", "e", "f", "segments.month"])})
    instance.cursor_field = None
    instance.google_ads_client = Obj(get_fields_metadata=query_object)
    schema = instance.get_json_schema()

    assert schema == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "type": "object",
        "properties": {
            "a": {"type": "string", "enum": ["a", "aa"]},
            "b": {"type": ["null", "array"], "items": {"type": "string", "enum": ["b", "bb"]}},
            "c": {"type": ["string", "null"]},
            "d": {"type": ["null", "array"], "items": {"type": ["string", "null"]}},
            "e": {"type": ["string", "null"]},
            "f": {"type": ["string", "null"]},
            "segments.month": {"type": ["string", "null"], "format": "date"},
        },
    }


@pytest.fixture
def mock_incremental_custom_query():
    """Create a mock IncrementalCustomQuery instance for testing."""
    config = {
        "table_name": "test_stream",
        "query": GAQL.parse("SELECT campaign.id FROM campaign"),
    }

    mock_api = Mock()
    mock_api.get_fields_metadata = Mock(return_value={})

    customers = [
        CustomerModel(id="1234567890", time_zone="UTC", is_manager_account=False, login_customer_id="9876543210"),
        CustomerModel(id="9876543210", time_zone="UTC", is_manager_account=True, login_customer_id=None),
    ]

    stream = IncrementalCustomQuery(
        config=config,
        api=mock_api,
        customers=customers,
        start_date="2024-01-01",
        conversion_window_days=14,
        end_date="2024-12-31",
    )

    return stream


class TestStateMigration:
    """Tests for CDK v7 concurrent state migration to legacy format."""

    def test_should_migrate_concurrent_state(self, mock_incremental_custom_query):
        """Test that concurrent state format is detected correctly."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {"customer_id": "customers/1234567890", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                }
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        assert mock_incremental_custom_query.should_migrate(concurrent_state) is True

    def test_should_not_migrate_legacy_state(self, mock_incremental_custom_query):
        """Test that legacy state format is not flagged for migration."""
        legacy_state = {"1234567890": {"segments.date": "2025-12-20"}, "9876543210": {"segments.date": "2025-12-21"}}

        assert mock_incremental_custom_query.should_migrate(legacy_state) is False

    def test_should_not_migrate_empty_state(self, mock_incremental_custom_query):
        """Test that empty state is not flagged for migration."""
        assert mock_incremental_custom_query.should_migrate({}) is False
        assert mock_incremental_custom_query.should_migrate(None) is False

    def test_migrate_concurrent_to_legacy_single_customer(self, mock_incremental_custom_query):
        """Test migration from concurrent to legacy format with single customer."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {"customer_id": "customers/1234567890", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                }
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        expected_legacy_state = {"1234567890": {"segments.date": "2025-12-20"}}

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == expected_legacy_state

    def test_migrate_concurrent_to_legacy_multiple_customers(self, mock_incremental_custom_query):
        """Test migration from concurrent to legacy format with multiple customers."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {"customer_id": "customers/1234567890", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                },
                {
                    "cursor": {"segments.date": "2025-12-21"},
                    "partition": {"customer_id": "customers/9876543210", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                },
                {
                    "cursor": {"segments.date": "2025-12-19"},
                    "partition": {"customer_id": "customers/5555555555", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                },
            ],
            "state": {"segments.date": "2025-12-19"},
        }

        expected_legacy_state = {
            "1234567890": {"segments.date": "2025-12-20"},
            "9876543210": {"segments.date": "2025-12-21"},
            "5555555555": {"segments.date": "2025-12-19"},
        }

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == expected_legacy_state

    def test_migrate_customer_id_without_prefix(self, mock_incremental_custom_query):
        """Test migration handles customer_id without 'customers/' prefix."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {
                        "customer_id": "1234567890",  # No "customers/" prefix
                        "parent_slice": {"customer_id": "9876543210", "parent_slice": {}},
                    },
                }
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        expected_legacy_state = {"1234567890": {"segments.date": "2025-12-20"}}

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == expected_legacy_state

    def test_migrate_returns_original_if_no_migration_needed(self, mock_incremental_custom_query):
        """Test that migrate returns original state if no migration needed."""
        legacy_state = {"1234567890": {"segments.date": "2025-12-20"}}

        migrated = mock_incremental_custom_query.migrate(legacy_state)
        assert migrated == legacy_state

    def test_state_setter_migrates_concurrent_state(self, mock_incremental_custom_query):
        """Test that state setter automatically migrates concurrent state."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {"customer_id": "customers/1234567890", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                }
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        mock_incremental_custom_query.state = concurrent_state

        # State should be migrated to legacy format
        assert "1234567890" in mock_incremental_custom_query.state
        assert mock_incremental_custom_query.state["1234567890"] == {"segments.date": "2025-12-20"}
        assert "states" not in mock_incremental_custom_query.state

    def test_state_setter_preserves_legacy_state(self, mock_incremental_custom_query):
        """Test that state setter preserves legacy state format."""
        legacy_state = {"1234567890": {"segments.date": "2025-12-20"}}

        mock_incremental_custom_query.state = legacy_state

        # State should remain in legacy format
        assert mock_incremental_custom_query.state == legacy_state

    def test_migrate_empty_states_array(self, mock_incremental_custom_query):
        """Test migration with empty states array."""
        concurrent_state = {"states": [], "state": {"segments.date": "2025-12-20"}}

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == {}

    def test_migrate_missing_cursor(self, mock_incremental_custom_query):
        """Test migration handles partition states without cursor."""
        concurrent_state = {
            "states": [
                {"partition": {"customer_id": "customers/1234567890", "parent_slice": {"customer_id": "9876543210", "parent_slice": {}}}}
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == {}

    def test_migrate_missing_customer_id(self, mock_incremental_custom_query):
        """Test migration handles partition states without customer_id."""
        concurrent_state = {
            "states": [
                {
                    "cursor": {"segments.date": "2025-12-20"},
                    "partition": {"parent_slice": {"customer_id": "9876543210", "parent_slice": {}}},
                }
            ],
            "state": {"segments.date": "2025-12-20"},
        }

        migrated = mock_incremental_custom_query.migrate(concurrent_state)
        assert migrated == {}
