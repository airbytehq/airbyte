#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

""" This is the example of input record for the test_tranform_data. """
input_test_data = [
    {
        "targetingCriteria": {
            "include": {
                "and": [
                    {
                        "or": {
                            "urn:li:adTargetingFacet:titles": [
                                "urn:li:title:100",
                                "urn:li:title:10326",
                                "urn:li:title:10457",
                                "urn:li:title:10738",
                                "urn:li:title:10966",
                                "urn:li:title:11349",
                                "urn:li:title:1159",
                            ]
                        }
                    },
                    {"or": {"urn:li:adTargetingFacet:locations": ["urn:li:geo:103644278"]}},
                    {"or": {"urn:li:adTargetingFacet:interfaceLocales": ["urn:li:locale:en_US"]}},
                ]
            },
            "exclude": {
                "or": {
                    "urn:li:adTargetingFacet:facet_Key1": [
                        "facet_test1",
                        "facet_test2",
                    ],
                    "urn:li:adTargetingFacet:facet_Key2": [
                        "facet_test3",
                        "facet_test4",
                    ],
                }
            },
        },
        "changeAuditStamps": {
            "created": {"time": 1629581275000},
            "lastModified": {"time": 1629664544760},
        },
        "dateRange": {
            "start": {"month": 8, "day": 13, "year": 2021},
            "end": {"month": 8, "day": 13, "year": 2021},
        },
        "variables": {
            "data": {
                "com.linkedin.ads.SponsoredUpdateCreativeVariables": {
                    "activity": "urn:li:activity:1234",
                    "directSponsoredContent": 0,
                    "share": "urn:li:share:1234",
                }
            }
        },
    }
]

""" This is the expected output from the `transform_data` method. """
output_test_data = [
    {
        "targetingCriteria": {
            "include": {
                "and": [
                    {
                        "type": "urn:li:adTargetingFacet:titles",
                        "values": [
                            "urn:li:title:100",
                            "urn:li:title:10326",
                            "urn:li:title:10457",
                            "urn:li:title:10738",
                            "urn:li:title:10966",
                            "urn:li:title:11349",
                            "urn:li:title:1159",
                        ],
                    },
                    {
                        "type": "urn:li:adTargetingFacet:locations",
                        "values": ["urn:li:geo:103644278"],
                    },
                    {
                        "type": "urn:li:adTargetingFacet:interfaceLocales",
                        "values": ["urn:li:locale:en_US"],
                    },
                ]
            },
            "exclude": {
                "or": [
                    {
                        "type": "urn:li:adTargetingFacet:facet_Key1",
                        "values": ["facet_test1", "facet_test2"],
                    },
                    {
                        "type": "urn:li:adTargetingFacet:facet_Key2",
                        "values": ["facet_test3", "facet_test4"],
                    },
                ]
            },
        },
        "variables": {
            "type": "com.linkedin.ads.SponsoredUpdateCreativeVariables",
            "values": [
                {"key": "activity", "value": "urn:li:activity:1234"},
                {"key": "directSponsoredContent", "value": 0},
                {"key": "share", "value": "urn:li:share:1234"},
            ],
        },
        "created": "2021-08-21 21:27:55",
        "lastModified": "2021-08-22 20:35:44",
        "start_date": "2021-08-13",
        "end_date": "2021-08-13",
    }
]
