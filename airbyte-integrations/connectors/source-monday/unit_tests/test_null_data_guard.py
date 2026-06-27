#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest


class TestMondayActivityExtractorNullData:
    """Tests for MondayActivityExtractor handling of null data in GraphQL error responses."""

    @pytest.mark.parametrize(
        ("response_body", "expected_record_count"),
        [
            pytest.param(
                {"data": None, "errors": [{"message": "Complexity budget exhausted"}]},
                0,
                id="null_data_with_errors",
            ),
            pytest.param(
                {"data": None},
                0,
                id="null_data_without_errors",
            ),
            pytest.param(
                {"errors": [{"message": "Internal server error"}]},
                0,
                id="missing_data_key_with_errors",
            ),
            pytest.param(
                {"data": {"boards": None}},
                0,
                id="null_boards",
            ),
            pytest.param(
                {"data": {"boards": []}},
                0,
                id="empty_boards",
            ),
        ],
    )
    def test_extract_records_handles_null_data(self, components_module, response_body, expected_record_count):
        """Verify extractor gracefully handles null/missing data without raising TypeError."""
        response = MagicMock()
        response.content = json.dumps(response_body).encode("utf-8")

        extractor = components_module.MondayActivityExtractor(parameters={})
        records = list(extractor.extract_records(response))

        assert len(records) == expected_record_count

    def test_extract_records_still_works_with_valid_data(self, components_module):
        """Verify the fix does not break normal extraction."""
        response = MagicMock()
        response_body = {
            "data": {"boards": [{"activity_logs": [{"data": '{"pulse_id": 456}', "entity": "pulse", "created_at": "16367386880000000"}]}]}
        }
        response.content = json.dumps(response_body).encode("utf-8")

        extractor = components_module.MondayActivityExtractor(parameters={})
        records = list(extractor.extract_records(response))

        assert len(records) == 1
        assert records[0]["pulse_id"] == 456


class TestItemPaginationStrategyNullData:
    """Tests for ItemPaginationStrategy handling of null data in GraphQL error responses."""

    @pytest.mark.parametrize(
        ("response_json", "expected"),
        [
            pytest.param(
                {"data": None, "errors": [{"message": "Complexity budget exhausted"}]},
                None,
                id="null_data_with_errors",
            ),
            pytest.param(
                {"data": None},
                None,
                id="null_data_without_errors",
            ),
        ],
    )
    def test_item_pagination_null_data(self, components_module, response_json, expected):
        """Verify paginator returns None (stop pagination) when data is null."""
        strategy = components_module.ItemPaginationStrategy(
            config={},
            page_size=1,
            parameters={"items_per_page": 1},
        )
        response = MagicMock()
        response.json.return_value = response_json

        result = strategy.next_page_token(
            response=response,
            last_page_size=0,
            last_record=None,
            last_page_token_value=None,
        )

        assert result == expected


class TestItemCursorPaginationStrategyNullData:
    """Tests for ItemCursorPaginationStrategy handling of null data in GraphQL error responses."""

    @pytest.mark.parametrize(
        ("response_json", "expected"),
        [
            pytest.param(
                {"data": None, "errors": [{"message": "Complexity budget exhausted"}]},
                None,
                id="null_data_with_errors",
            ),
            pytest.param(
                {"data": None},
                None,
                id="null_data_without_errors",
            ),
        ],
    )
    def test_item_cursor_pagination_null_data(self, components_module, response_json, expected):
        """Verify cursor paginator returns None (stop pagination) when data is null."""
        strategy = components_module.ItemCursorPaginationStrategy(
            config={},
            page_size=1,
            parameters={"items_per_page": 1},
        )
        response = MagicMock()
        response.json.return_value = response_json

        result = strategy.next_page_token(
            response=response,
            last_page_size=0,
            last_record=None,
            last_page_token_value=None,
        )

        assert result == expected
