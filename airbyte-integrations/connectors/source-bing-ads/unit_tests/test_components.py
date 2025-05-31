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
        "test_name,input_record,expected_settings",
        [
            (
                "string_id_conversion_with_details",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "AccountId": "12345",
                            "CampaignIds": ["67890"],  # List, not string
                            "PageFeedIds": [],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "AccountId": 12345,
                            "CampaignIds": ["67890"],  # List stays as list
                            "PageFeedIds": None,
                        }
                    ]
                },
            ),
            (
                "string_id_conversion_without_details",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "AccountId": "98765",
                            "AdGroupIds": ["11111", "22222"],  # List, not string
                            "CustomerId": "33333",
                            "NonIdField": "should_not_convert",
                            "EmptyList": [],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "AccountId": 98765,
                            "AdGroupIds": ["11111", "22222"],  # List stays as list
                            "CustomerId": 33333,
                            "NonIdField": "should_not_convert",
                            "EmptyList": None,
                        }
                    ]
                },
            ),
            (
                "mixed_id_types",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "AccountId": "12345",  # string -> int
                            "CampaignId": 67890,  # already int -> stays int
                            "AdGroupIds": "invalid_number",  # string but doesn't end with "Id" -> stays string
                            "KeywordId": 99999,  # already int -> stays int
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "AccountId": 12345,
                            "CampaignId": 67890,
                            "AdGroupIds": "invalid_number",  # Not converted (doesn't end with "Id")
                            "KeywordId": 99999,
                        }
                    ]
                },
            ),
            (
                "edge_case_id_fields",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "CustomSetting",
                            "Id": "123456",  # ends with Id -> convert
                            "MyId": "345678",  # ends with Id -> convert
                            "AccountId": "456789",  # ends with Id -> convert
                            "Identity": "567890",  # ends with "ity", not "Id" -> don't convert
                            "NotAnId": "333444",  # ends with Id -> convert
                            "Ids": "789012",  # doesn't end with "Id" -> don't convert
                            "Ideas": "111222",  # doesn't end with "Id" -> don't convert
                            "AlsoNotIds": "555666",  # doesn't end with "Id" -> don't convert
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "CustomSetting",
                            "Id": 123456,
                            "MyId": 345678,
                            "AccountId": 456789,
                            "Identity": "567890",  # Not converted (ends with "ity")
                            "NotAnId": 333444,  # Converted (ends with "Id")
                            "Ids": "789012",  # Not converted
                            "Ideas": "111222",  # Not converted
                            "AlsoNotIds": "555666",  # Not converted
                        }
                    ]
                },
            ),
        ],
    )
    def test_string_id_conversion(self, test_name, input_record, expected_settings):
        """Test string to integer conversion for keys ending with 'Id'."""
        self.transformer.transform(input_record)
        assert input_record["Settings"] == expected_settings

    @pytest.mark.parametrize(
        "test_name,input_record,expected_settings",
        [
            (
                "page_feed_ids_list_of_strings_with_details",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "PageFeedIds": ["8246337222870", "8246337224338"],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "PageFeedIds": {"long": [8246337222870, 8246337224338]},
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_list_of_strings_without_details",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": ["1234567890123", "9876543210987"],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": {"long": [1234567890123, 9876543210987]},
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_single_string_item",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Location"}],
                            "PageFeedIds": ["5555666677778888"],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Location"}]},
                            "PageFeedIds": {"long": [5555666677778888]},
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_empty_list",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "PageFeedIds": [],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "PageFeedIds": None,
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_none_value",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": None,
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": None,
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_missing_field",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "AccountId": "12345",
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "AccountId": 12345,
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_mixed_with_other_fields",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "AccountId": "98765",
                            "PageFeedIds": ["1111222233334444", "5555666677778888"],
                            "CampaignId": "11111",
                            "EmptyList": [],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "AccountId": 98765,
                            "PageFeedIds": {"long": [1111222233334444, 5555666677778888]},
                            "CampaignId": 11111,
                            "EmptyList": None,
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_invalid_conversion",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": ["invalid_number", "not_a_number"],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": ["invalid_number", "not_a_number"],
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_mixed_valid_invalid",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Location"}],
                            "PageFeedIds": ["1234567890", "invalid", "9876543210"],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Location"}]},
                            "PageFeedIds": ["1234567890", "invalid", "9876543210"],
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_non_string_items",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": [123456789, "987654321", None],
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "PerformanceMaxSetting",
                            "PageFeedIds": {"long": [987654321]},
                        }
                    ]
                },
            ),
            (
                "page_feed_ids_already_object_format",
                {
                    "Id": 486441589,
                    "Settings": [
                        {
                            "Type": "TargetSetting",
                            "Details": [{"CriterionTypeGroup": "Audience"}],
                            "PageFeedIds": {"long": [1234567890, 9876543210]},
                        }
                    ],
                },
                {
                    "Setting": [
                        {
                            "Type": "TargetSetting",
                            "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience"}]},
                            "PageFeedIds": {"long": [1234567890, 9876543210]},
                        }
                    ]
                },
            ),
        ],
    )
    def test_page_feed_ids_transformation(self, test_name, input_record, expected_settings):
        """Test PageFeedIds list to object transformation."""
        self.transformer.transform(input_record)
        assert input_record["Settings"] == expected_settings

    @pytest.mark.parametrize(
        "test_name,input_value,expected_output",
        [
            (
                "valid_list_of_string_ids",
                ["8246337222870", "8246337224338", "1234567890"],
                {"long": [8246337222870, 8246337224338, 1234567890]},
            ),
            (
                "single_string_id",
                ["9876543210987"],
                {"long": [9876543210987]},
            ),
            (
                "empty_list",
                [],
                [],
            ),
            (
                "none_value",
                None,
                None,
            ),
            (
                "non_list_value",
                "not_a_list",
                "not_a_list",
            ),
            (
                "list_with_invalid_strings",
                ["invalid", "not_a_number"],
                ["invalid", "not_a_number"],
            ),
            (
                "mixed_valid_invalid_strings",
                ["1234567890", "invalid", "9876543210"],
                ["1234567890", "invalid", "9876543210"],
            ),
            (
                "list_with_non_string_items",
                [123456789, "987654321", None],
                {"long": [987654321]},
            ),
            (
                "list_with_empty_strings",
                ["", "1234567890", ""],
                ["", "1234567890", ""],
            ),
            (
                "large_numbers",
                ["999999999999999999", "111111111111111111"],
                {"long": [999999999999999999, 111111111111111111]},
            ),
        ],
    )
    def test_convert_page_feed_id_lists_helper(self, test_name, input_value, expected_output):
        """Test the _convert_page_feed_id_lists helper method directly."""
        result = self.transformer._convert_page_feed_id_lists(input_value)
        assert result == expected_output

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

    def test_combined_transformations_with_id_conversion(self):
        """Test that Settings, BiddingScheme, and ID conversion work together."""
        input_record = {
            "Id": 486441589,
            "Settings": [
                {
                    "Type": "TargetSetting",
                    "Details": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}],
                    "AccountId": "12345",
                    "CampaignIds": ["67890"],  # List, not string
                    "PageFeedIds": [],
                    "NonIdField": "should_not_convert",
                }
            ],
            "BiddingScheme": {"Type": "TargetCpa", "TargetCpa": 40, "MaxCpc": {"Amount": 9}},
        }

        self.transformer.transform(input_record)

        # Check Settings transformation with ID conversion
        expected_settings = {
            "Setting": [
                {
                    "Type": "TargetSetting",
                    "Details": {"TargetSettingDetail": [{"CriterionTypeGroup": "Audience", "TargetAndBid": False}]},
                    "AccountId": 12345,
                    "CampaignIds": ["67890"],  # List stays as list
                    "PageFeedIds": None,
                    "NonIdField": "should_not_convert",
                }
            ]
        }
        assert input_record["Settings"] == expected_settings

        # Check BiddingScheme transformation
        expected_bidding_scheme = {"Type": "TargetCpa", "TargetCpa": 40.0, "MaxCpc": {"Amount": 9.0}}
        assert input_record["BiddingScheme"] == expected_bidding_scheme
