# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock as rm

from airbyte_cdk.sources.declarative.types import StreamSlice


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
def test_settings_transformation(test_name, input_record, expected_settings, components_module):
    """Test various Settings field transformations."""
    transformer = components_module.BingAdsCampaignsRecordTransformer()
    transformer.transform(input_record)
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


@pytest.mark.parametrize(
    "stream_state,expected_state",
    (
        (
            {
                "1111111": {"Modified Time": "2025-01-01T01:01:55.111+00:00"},
                "Id": "1111111",
                "Match Type": None,
                "Modified Time": None,
            },
            {"1111111": {"Modified Time": "2025-01-01T01:01:55.111+00:00"}},
        ),
        ({"1111111": {"Modified Time": "2025-01-01T01:01:55.111+00:00"}}, {"1111111": {"Modified Time": "2025-01-01T01:01:55.111+00:00"}}),
        (
            {
                "states": [
                    {"partition": {"account_id": "account_id"}, "cursor": {"Modified Time": "2025-01-01T01:01:55.111+00:00"}},
                ],
                "state": {"Modified Time": "2025-06-06T05:13:54.447+00:00"},
            },
            {
                "state": {"Modified Time": "2025-06-06T05:13:54.447+00:00"},
                "states": [{"cursor": {"Modified Time": "2025-01-01T01:01:55.111+00:00"}, "partition": {"account_id": "account_id"}}],
            },
        ),
    ),
)
def test_bulk_stream_state_migration(stream_state, expected_state, components_module):
    migrator = components_module.BulkStreamsStateMigration()
    assert migrator.migrate(stream_state) == expected_state


import gzip
import io
from types import SimpleNamespace


def _make_csv_bytes(rows_text: str, encoding: str = "utf-8") -> bytes:
    return rows_text.encode(encoding)


def _gzip_bytes(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(data)
    return buf.getvalue()


def _make_raw_stream(data: bytes):
    stream = io.BytesIO(data)
    stream.auto_close = True
    return stream


def _make_response(data: bytes):
    return SimpleNamespace(raw=_make_raw_stream(data))


CSV_TWO_ROWS = "name,value\nalice,1\nbob,2\n"
CSV_SINGLE_ROW = "name,value\nalice,1\n"


@pytest.mark.parametrize(
    "prefix,stream_data,read_size,expected",
    [
        pytest.param(b"\x1f\x8b", b"rest", -1, b"\x1f\x8brest", id="unbounded_read"),
        pytest.param(b"\x1f\x8b", b"rest", 1, b"\x1f", id="bounded_within_prefix"),
        pytest.param(b"\x1f\x8b", b"rest", 3, b"\x1f\x8br", id="bounded_spanning_prefix_and_stream"),
        pytest.param(b"\x1f\x8b", b"rest", 2, b"\x1f\x8b", id="bounded_exact_prefix_length"),
        pytest.param(b"AB", b"", 5, b"AB", id="stream_empty"),
        pytest.param(b"", b"hello", -1, b"hello", id="empty_prefix"),
        pytest.param(b"", b"hello", 3, b"hel", id="empty_prefix_bounded"),
        pytest.param(b"\x1f\x8b", b"rest", 0, b"", id="zero_size"),
    ],
)
def test_prefixed_stream_read(prefix, stream_data, read_size, expected, components_module):
    stream = components_module._PrefixedStream(prefix, io.BytesIO(stream_data))
    assert stream.read(read_size) == expected


def test_prefixed_stream_sequential_reads(components_module):
    stream = components_module._PrefixedStream(b"AB", io.BytesIO(b"CDEF"))
    assert stream.read(1) == b"A"
    assert stream.read(1) == b"B"
    assert stream.read(2) == b"CD"
    assert stream.read(-1) == b"EF"
    assert stream.read(-1) == b""


def test_prefixed_stream_readinto(components_module):
    stream = components_module._PrefixedStream(b"AB", io.BytesIO(b"CD"))
    buf = bytearray(4)
    n = stream.readinto(buf)
    assert n == 4
    assert buf == bytearray(b"ABCD")


def test_prefixed_stream_readable(components_module):
    stream = components_module._PrefixedStream(b"", io.BytesIO(b""))
    assert stream.readable() is True


def test_decoder_is_stream_response(components_module):
    decoder = components_module.BingAdsGzipCsvDecoder()
    assert decoder.is_stream_response() is True


@pytest.mark.parametrize(
    "csv_text,use_gzip,expected_rows",
    [
        pytest.param(
            CSV_TWO_ROWS,
            True,
            [{"name": "alice", "value": "1"}, {"name": "bob", "value": "2"}],
            id="gzipped_csv",
        ),
        pytest.param(
            CSV_TWO_ROWS,
            False,
            [{"name": "alice", "value": "1"}, {"name": "bob", "value": "2"}],
            id="plain_csv",
        ),
        pytest.param(
            CSV_SINGLE_ROW,
            True,
            [{"name": "alice", "value": "1"}],
            id="gzipped_csv_with_bom",
        ),
        pytest.param(
            CSV_SINGLE_ROW,
            False,
            [{"name": "alice", "value": "1"}],
            id="plain_csv_with_bom",
        ),
        pytest.param(
            "col_a,col_b\n",
            True,
            [],
            id="gzipped_header_only",
        ),
        pytest.param(
            "col_a,col_b\n",
            False,
            [],
            id="plain_header_only",
        ),
    ],
)
def test_decoder_decode(csv_text, use_gzip, expected_rows, components_module):
    raw_csv = csv_text.encode("utf-8-sig")
    data = _gzip_bytes(raw_csv) if use_gzip else raw_csv
    response = _make_response(data)
    rows = list(components_module.BingAdsGzipCsvDecoder().decode(response))
    assert rows == expected_rows


def test_decoder_decode_empty_response(components_module):
    response = _make_response(b"")
    rows = list(components_module.BingAdsGzipCsvDecoder().decode(response))
    assert rows == []


def test_decoder_closes_raw_stream(components_module):
    response = _make_response(_gzip_bytes(b"a,b\n1,2\n"))
    raw = response.raw
    list(components_module.BingAdsGzipCsvDecoder().decode(response))
    assert raw.closed


def test_decoder_logs_error_and_yields_empty_on_bad_data(components_module):
    response = _make_response(b"\x1f\x8b not valid gzip at all")
    rows = list(components_module.BingAdsGzipCsvDecoder().decode(response))
    assert rows == [{}]


# --- BingAdsReportDownloadRequester tests ---


POLL_URL = "https://reporting.api.bingads.microsoft.com/Reporting/v13/GenerateReport/Poll"
FRESH_SAS_URL = "https://blobstorage.blob.core.windows.net/report?sv=2024&sig=fresh_token"
STALE_SAS_URL = "https://blobstorage.blob.core.windows.net/report?sv=2024&sig=stale_token"


def _make_stream_slice(report_request_id="REQ-123", account_id="ACC-1", parent_customer_id="CUST-1"):
    return StreamSlice(
        partition={"account_id": account_id},
        cursor_slice={},
        extra_fields={
            "creation_response": {"ReportRequestId": report_request_id},
            "ParentCustomerId": parent_customer_id,
            "download_target": STALE_SAS_URL,
        },
    )


def _build_requester(components_module, config=None, authenticator=None):
    """Build a BingAdsReportDownloadRequester with minimal required fields."""
    cfg = config or {"developer_token": "fake_dev_token"}
    return components_module.BingAdsReportDownloadRequester(
        name="test_download_requester",
        url_base="{{download_target}}",
        config=cfg,
        parameters={},
        report_poll_authenticator=authenticator,
    )


class _FakeAuthenticator:
    """Minimal stub that satisfies the get_auth_header interface."""

    def get_auth_header(self):
        return {"Authorization": "Bearer fake_access_token"}


@pytest.mark.parametrize(
    "poll_response_json,expected_url",
    [
        pytest.param(
            {"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": FRESH_SAS_URL}},
            FRESH_SAS_URL,
            id="successful_repoll_returns_fresh_url",
        ),
        pytest.param(
            {"ReportRequestStatus": {"Status": "Success"}},
            None,
            id="repoll_without_download_url_returns_none",
        ),
        pytest.param(
            {},
            None,
            id="empty_repoll_response_returns_none",
        ),
    ],
)
def test_get_fresh_download_url(poll_response_json, expected_url, components_module):
    requester = _build_requester(components_module, authenticator=_FakeAuthenticator())
    stream_slice = _make_stream_slice()

    with rm.Mocker() as m:
        m.post(POLL_URL, json=poll_response_json, status_code=200)
        result = requester._get_fresh_download_url(stream_slice)

    assert result == expected_url

    if expected_url:
        sent_request = m.last_request
        assert sent_request.json() == {"ReportRequestId": "REQ-123"}
        assert sent_request.headers["Authorization"] == "Bearer fake_access_token"
        assert sent_request.headers["DeveloperToken"] == "fake_dev_token"
        assert sent_request.headers["CustomerAccountId"] == "ACC-1"
        assert sent_request.headers["CustomerId"] == "CUST-1"


def test_get_fresh_download_url_falls_back_on_http_error(components_module):
    requester = _build_requester(components_module, authenticator=_FakeAuthenticator())
    stream_slice = _make_stream_slice()

    with rm.Mocker() as m:
        m.post(POLL_URL, status_code=500)
        result = requester._get_fresh_download_url(stream_slice)

    assert result is None


def test_get_fresh_download_url_falls_back_on_connection_error(components_module):
    requester = _build_requester(components_module, authenticator=_FakeAuthenticator())
    stream_slice = _make_stream_slice()

    with rm.Mocker() as m:
        m.post(POLL_URL, exc=requests.ConnectionError("network failure"))
        result = requester._get_fresh_download_url(stream_slice)

    assert result is None


def test_get_fresh_download_url_returns_none_without_report_request_id(components_module):
    requester = _build_requester(components_module)
    stream_slice = StreamSlice(
        partition={"account_id": "ACC-1"},
        cursor_slice={},
        extra_fields={"creation_response": {}, "ParentCustomerId": "CUST-1"},
    )

    result = requester._get_fresh_download_url(stream_slice)
    assert result is None


def test_get_fresh_download_url_works_without_authenticator(components_module):
    requester = _build_requester(components_module, authenticator=None)
    stream_slice = _make_stream_slice()

    with rm.Mocker() as m:
        m.post(
            POLL_URL,
            json={"ReportRequestStatus": {"Status": "Success", "ReportDownloadUrl": FRESH_SAS_URL}},
            status_code=200,
        )
        result = requester._get_fresh_download_url(stream_slice)

    assert result == FRESH_SAS_URL
    assert "Authorization" not in m.last_request.headers


# --- send_request() integration tests ---


def test_send_request_forwards_fresh_url(components_module):
    """send_request() should replace download_target with the fresh URL from re-poll."""
    requester = _build_requester(components_module, authenticator=_FakeAuthenticator())
    stream_slice = _make_stream_slice()

    with patch.object(requester, "_get_fresh_download_url", return_value=FRESH_SAS_URL):
        with patch(
            "airbyte_cdk.sources.declarative.requesters.http_requester.HttpRequester.send_request",
            return_value=MagicMock(),
        ) as mock_super_send:
            requester.send_request(stream_slice=stream_slice)

    forwarded_slice = mock_super_send.call_args.kwargs["stream_slice"]
    assert forwarded_slice.extra_fields["download_target"] == FRESH_SAS_URL


def test_send_request_keeps_original_url_when_repoll_returns_none(components_module):
    """send_request() should forward the original stream_slice when re-poll returns None."""
    requester = _build_requester(components_module, authenticator=_FakeAuthenticator())
    stream_slice = _make_stream_slice()

    with patch.object(requester, "_get_fresh_download_url", return_value=None):
        with patch(
            "airbyte_cdk.sources.declarative.requesters.http_requester.HttpRequester.send_request",
            return_value=MagicMock(),
        ) as mock_super_send:
            requester.send_request(stream_slice=stream_slice)

    forwarded_slice = mock_super_send.call_args.kwargs["stream_slice"]
    assert forwarded_slice.extra_fields["download_target"] == STALE_SAS_URL


def test_get_fresh_download_url_falls_back_on_auth_error(components_module):
    """Auth failures inside _get_fresh_download_url should fall back, not bubble up."""

    class _RaisingAuthenticator:
        def get_auth_header(self):
            raise RuntimeError("token refresh exploded")

    requester = _build_requester(components_module, authenticator=_RaisingAuthenticator())
    stream_slice = _make_stream_slice()

    result = requester._get_fresh_download_url(stream_slice)
    assert result is None


# --- Manifest-level integration test (P1) ---


def test_manifest_instantiates_custom_download_requester(config):
    """Verify the CustomRequester factory path produces a correctly wired BingAdsReportDownloadRequester.

    This test builds the full source from manifest.yaml via YamlDeclarativeSource,
    finds a report stream, and asserts that:
    1. The download requester is an instance of BingAdsReportDownloadRequester.
    2. stream_response is True (derived from decoder in __post_init__).
    3. The report_poll_authenticator is resolved and has get_auth_header().
    """
    from pathlib import Path

    from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
    from airbyte_cdk.test.catalog_builder import CatalogBuilder
    from airbyte_cdk.test.state_builder import StateBuilder

    yaml_path = Path(__file__).parent.parent / "manifest.yaml"
    catalog = CatalogBuilder().build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(yaml_path), catalog=catalog, config=config, state=state)

    # Find a report stream that uses the async retriever with download_requester
    target_stream = None
    for stream in source.streams(config=config):
        if stream.name == "account_performance_report_daily":
            target_stream = stream
            break
    assert target_stream is not None, "account_performance_report_daily stream not found"

    # Navigate to the AsyncJobPartitionRouter (stream_slicer).
    # The CDK may wrap the stream as a concurrent DefaultStream or leave it as a
    # DeclarativeStream depending on config/version, so handle both paths.
    if hasattr(target_stream, "retriever"):
        # DeclarativeStream path (non-concurrent)
        slicer = target_stream.retriever.stream_slicer
    else:
        # DefaultStream path (concurrent wrapper)
        slicer = target_stream._stream_partition_generator._stream_slicer

    factory_fn = slicer._job_orchestrator_factory
    job_repository = None
    for var_name, cell in zip(factory_fn.__code__.co_freevars, factory_fn.__closure__):
        if var_name == "job_repository":
            job_repository = cell.cell_contents
            break
    assert job_repository is not None, "Could not find job_repository in factory closure"

    download_requester = job_repository.download_retriever.requester

    # Assert the requester is our custom class (not plain HttpRequester)
    import components as components_mod

    assert isinstance(download_requester, components_mod.BingAdsReportDownloadRequester)

    # Assert stream_response is True (critical for streaming decoders)
    assert download_requester.stream_response is True

    # Assert report_poll_authenticator is resolved and usable
    assert download_requester.report_poll_authenticator is not None
    assert hasattr(download_requester.report_poll_authenticator, "get_auth_header")
