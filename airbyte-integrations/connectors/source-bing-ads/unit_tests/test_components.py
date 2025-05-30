# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from source_bing_ads.components import BingAdsCampaignsRecordTransformer


class TestBingAdsCampaignsRecordTransformer:
    """Test cases for the BingAdsCampaignsRecordTransformer component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = BingAdsCampaignsRecordTransformer()

    @pytest.mark.parametrize(
        "test_name,input_record,expected_settings",
        [
            (
                "settings_with_target_setting_details",
                {
                    "Id": 486441589,
                    "Settings": [{"Type": "TargetSetting", "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]}],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                        }
                    ]
                },
            ),
            (
                "settings_with_performance_max_setting",
                {"Id": 486441589, "Settings": [{"Type": "PerformanceMaxSetting", "FinalUrlExpansionOptOut": False}]},
                {"Setting": [{"Type": "PerformanceMaxSetting", "FinalUrlExpansionOptOut": False}]},
            ),
            (
                "settings_with_mixed_types",
                {
                    "Id": 486441589,
                    "Settings": [
                        {"Type": "PerformanceMaxSetting", "FinalUrlExpansionOptOut": False},
                        {"Type": "TargetSetting", "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                    ],
                },
                {
                    "Setting": [
                        {"Type": "PerformanceMaxSetting", "FinalUrlExpansionOptOut": False},
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                        },
                    ]
                },
            ),
            (
                "settings_with_additional_properties",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}],
                            "CustomProperty": "CustomValue",
                            "AnotherProperty": 123,
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                            "CustomProperty": "CustomValue",
                            "AnotherProperty": 123,
                        }
                    ]
                },
            ),
            (
                "non_dict_setting_items",
                {
                    "Id": 486441589,
                    "Settings": [
                        "invalid_setting",
                        {"Type": "TargetSetting", "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                        123,
                    ],
                },
                {
                    "Setting": [
                        "invalid_setting",
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                        },
                        123,
                    ]
                },
            ),
            (
                "setting_with_empty_details",
                {"Id": 486441589, "Settings": [{"Type": "TargetSetting", "Details": []}]},
                {"Setting": [{"Type": "TargetSetting", "Details": {"TargetSettingDetail": []}}]},
            ),
            (
                "setting_with_none_details",
                {"Id": 486441589, "Settings": [{"Type": "TargetSetting", "Details": None}]},
                {"Setting": [{"Type": "TargetSetting", "Details": None}]},
            ),
            (
                "setting_without_type_field",
                {
                    "Id": 486441589,
                    "Settings": [{"Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}], "CustomField": "value"}],
                },
                {
                    "Setting": [
                        {
                            "Type": None,
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                            "CustomField": "value",
                        }
                    ]
                },
            ),
            (
                "complex_details_structure",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [
                                {
                                    "CriterionTypeGroup": "Audience",
                                    "TargetAndBid": False,
                                    "NestedObject": {"Property1": "Value1", "Property2": ["item1", "item2"]},
                                },
                                {"CriterionTypeGroup": "Location", "TargetAndBid": True},
                            ],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {
                                "TargetSettingDetail": [
                                    {
                                        "CriterionTypeGroup": "Audience",
                                        "TargetAndBid": False,
                                        "NestedObject": {"Property1": "Value1", "Property2": ["item1", "item2"]},
                                    },
                                    {"CriterionTypeGroup": "Location", "TargetAndBid": True},
                                ]
                            },
                        }
                    ]
                },
            ),
        ],
    )
    def test_settings_transformation(self, test_name, input_record, expected_settings):
        """Test various Settings field transformations."""
        self.transformer.transform(input_record)
        assert input_record["Settings"] == expected_settings

    @pytest.mark.parametrize(
        "test_name,input_record",
        [
            ("empty_settings_list", {"Id": 486441589, "Settings": []}),
            ("none_settings", {"Id": 486441589, "Settings": None}),
            ("missing_settings_field", {"Id": 486441589, "Name": "Test Campaign"}),
            ("non_list_settings", {"Id": 486441589, "Settings": "invalid_value"}),
        ],
    )
    def test_settings_unchanged(self, test_name, input_record):
        """Test that certain Settings configurations remain unchanged."""
        original_settings = input_record.get("Settings")
        original_keys = set(input_record.keys())

        self.transformer.transform(input_record)

        # Settings should remain unchanged
        assert input_record.get("Settings") == original_settings
        # No new keys should be added
        assert set(input_record.keys()) == original_keys

    @pytest.mark.parametrize(
        "test_name,input_record,expected_bidding_scheme",
        [
            (
                "bidding_scheme_with_integer_maxcpc_amount",
                {
                    "Id": 486441589,
                    "BiddingScheme": {"Type": "ManualCpc", "MaxCpc": {"Amount": 9}},
                },
                {"Type": "ManualCpc", "MaxCpc": {"Amount": 9.0}},
            ),
            (
                "bidding_scheme_with_float_maxcpc_amount",
                {
                    "Id": 486441589,
                    "BiddingScheme": {"Type": "ManualCpc", "MaxCpc": {"Amount": 2.01}},
                },
                {"Type": "ManualCpc", "MaxCpc": {"Amount": 2.01}},
            ),
            (
                "bidding_scheme_with_integer_target_cpa",
                {
                    "Id": 486441589,
                    "BiddingScheme": {"Type": "TargetCpa", "TargetCpa": 40, "MaxCpc": {"Amount": 2.01}},
                },
                {"Type": "TargetCpa", "TargetCpa": 40.0, "MaxCpc": {"Amount": 2.01}},
            ),
            (
                "bidding_scheme_multiple_integer_values",
                {
                    "Id": 486441589,
                    "BiddingScheme": {
                        "Type": "TargetRoas",
                        "TargetRoas": 300,
                        "MaxCpc": {"Amount": 5},
                        "MinCpc": {"Amount": 1},
                    },
                },
                {
                    "Type": "TargetRoas",
                    "TargetRoas": 300.0,
                    "MaxCpc": {"Amount": 5.0},
                    "MinCpc": {"Amount": 1.0},
                },
            ),
            (
                "bidding_scheme_no_integers",
                {
                    "Id": 486441589,
                    "BiddingScheme": {"Type": "EnhancedCpc", "MaxCpc": {"Amount": 2.5}},
                },
                {"Type": "EnhancedCpc", "MaxCpc": {"Amount": 2.5}},
            ),
            (
                "bidding_scheme_with_string_values",
                {
                    "Id": 486441589,
                    "BiddingScheme": {"Type": "ManualCpc", "Strategy": "aggressive", "MaxCpc": {"Amount": 10}},
                },
                {"Type": "ManualCpc", "Strategy": "aggressive", "MaxCpc": {"Amount": 10.0}},
            ),
            (
                "bidding_scheme_deeply_nested",
                {
                    "Id": 486441589,
                    "BiddingScheme": {
                        "Type": "Custom",
                        "Config": {"Level1": {"Level2": {"IntValue": 25, "FloatValue": 25.5}}},
                    },
                },
                {
                    "Type": "Custom",
                    "Config": {"Level1": {"Level2": {"IntValue": 25.0, "FloatValue": 25.5}}},
                },
            ),
        ],
    )
    def test_bidding_scheme_transformation(self, test_name, input_record, expected_bidding_scheme):
        """Test BiddingScheme integer to float conversions."""
        self.transformer.transform(input_record)
        assert input_record["BiddingScheme"] == expected_bidding_scheme

    @pytest.mark.parametrize(
        "test_name,input_record",
        [
            ("none_bidding_scheme", {"Id": 486441589, "BiddingScheme": None}),
            ("missing_bidding_scheme", {"Id": 486441589, "Name": "Test Campaign"}),
            ("non_dict_bidding_scheme", {"Id": 486441589, "BiddingScheme": "invalid_value"}),
            ("empty_bidding_scheme", {"Id": 486441589, "BiddingScheme": {}}),
        ],
    )
    def test_bidding_scheme_unchanged(self, test_name, input_record):
        """Test that certain BiddingScheme configurations remain unchanged."""
        original_bidding_scheme = input_record.get("BiddingScheme")
        original_keys = set(input_record.keys())

        self.transformer.transform(input_record)

        # BiddingScheme should remain unchanged
        assert input_record.get("BiddingScheme") == original_bidding_scheme
        # No new keys should be added
        assert set(input_record.keys()) == original_keys

    def test_combined_settings_and_bidding_scheme_transformation(self):
        """Test that both Settings and BiddingScheme transformations work together."""
        input_record = {
            "Id": 486441589,
            "Settings": [{"Type": "TargetSetting", "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]}],
            "BiddingScheme": {"Type": "TargetCpa", "TargetCpa": 40, "MaxCpc": {"Amount": 9}},
        }

        self.transformer.transform(input_record)

        # Check Settings transformation
        expected_settings = {
            "Setting": [
                {
                    "Type": "TargetSetting",
                    "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                }
            ]
        }
        assert input_record["Settings"] == expected_settings

        # Check BiddingScheme transformation
        expected_bidding_scheme = {"Type": "TargetCpa", "TargetCpa": 40.0, "MaxCpc": {"Amount": 9.0}}
        assert input_record["BiddingScheme"] == expected_bidding_scheme
