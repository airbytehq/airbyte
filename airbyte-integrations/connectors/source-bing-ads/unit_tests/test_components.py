# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from source_bing_ads.components import CampaignsSettingsTransformer


class TestCampaignsSettingsTransformer:
    """Test cases for the CampaignsSettingsTransformer component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = CampaignsSettingsTransformer()

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
