#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader

from .conftest import get_source


class TestConfigTransformations:
    def test_given_valid_config_returns_expected_config(self, config):
        copy_config = config.copy()

        source = get_source(copy_config)

        source.write_config = Mock()
        transformed_config = source.configure(config, "/not/a/path/")
        assert transformed_config.get("end_date") is None
        customer_ids = transformed_config.get("customer_ids")
        assert isinstance(customer_ids, list)
        assert customer_ids == ["123", "456", "789"]

    def test_given_conditions_not_met_returns_input_config(self, config, components_module):
        copy_config = config.copy()
        copy_config["end_date"] = "2025-07-25"
        del copy_config["customer_id"]
        source = get_source(copy_config)

        source.write_config = Mock()
        transformed_config = source.configure(config, "/not/a/path/")

        assert transformed_config == copy_config


class TestConfigValidations:
    def test_given_valid_custom_queries_returns_expected_streams(self, config):
        copy_config = config.copy()

        source = get_source(copy_config)

        source.write_config = Mock()
        transformed_config = source.configure(config, "/not/a/path/")

        stream_names = [stream.name for stream in source.streams(config=transformed_config)]

        assert "happytable" in stream_names
        assert "unhappytable" in stream_names
        assert "ad_group_custom" in stream_names

    @pytest.mark.parametrize(
        "query",
        [
            "campaign.name FROM campaign_budget",
            "SELECT FROM campaign_budget WHERE segments.date = '2021-01-01'",
            "SELECT campaign.name WHERE segments.date '2021-01-01'",
            "SELECT fie ld1, field2 FROM table",
        ],
        ids=["malformed_query_1", "malformed_query_2", "malformed_query_3", "malformed_query_4"],
    )
    def test_given_invalid_custom_queries_raises(self, config_for_custom_query_tests, query):
        copy_config = config_for_custom_query_tests.copy()
        copy_config["custom_queries_array"][0]["query"] = query
        source = get_source(copy_config)

        with pytest.raises(AirbyteTracedException):
            source.streams(config=copy_config)
