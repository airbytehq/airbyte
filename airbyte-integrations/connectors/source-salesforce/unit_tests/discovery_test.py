#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from source_salesforce.api import DATE_TYPES, LOOSE_TYPES, NUMBER_TYPES, STRING_TYPES, Salesforce
from source_salesforce.exceptions import TypeSalesforceException


@pytest.mark.parametrize(
    "streams_criteria,predicted_filtered_streams",
    [
        ([{"criteria": "exacts", "value": "Account"}], ["Account"]),
        (
            [{"criteria": "not exacts", "value": "CustomStreamHistory"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory", "CustomStream"],
        ),
        ([{"criteria": "starts with", "value": "lead"}], ["Leads", "LeadHistory"]),
        (
            [{"criteria": "starts not with", "value": "custom"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory"],
        ),
        ([{"criteria": "ends with", "value": "story"}], ["LeadHistory", "OrderHistory", "CustomStreamHistory"]),
        ([{"criteria": "ends not with", "value": "s"}], ["Account", "LeadHistory", "OrderHistory", "CustomStream", "CustomStreamHistory"]),
        ([{"criteria": "contains", "value": "applicat"}], ["AIApplications"]),
        ([{"criteria": "contains", "value": "hist"}], ["LeadHistory", "OrderHistory", "CustomStreamHistory"]),
        (
            [{"criteria": "not contains", "value": "stream"}],
            ["Account", "AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory"],
        ),
        (
            [{"criteria": "not contains", "value": "Account"}],
            ["AIApplications", "Leads", "LeadHistory", "Orders", "OrderHistory", "CustomStream", "CustomStreamHistory"],
        ),
    ],
)
def test_discover_with_streams_criteria_param(streams_criteria, predicted_filtered_streams, stream_config):
    updated_config = {**stream_config, **{"streams_criteria": streams_criteria}}
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"
    sf_object.describe = Mock(
        return_value={
            "sobjects": [
                {"name": "Account", "queryable": True},
                {"name": "AIApplications", "queryable": True},
                {"name": "Leads", "queryable": True},
                {"name": "LeadHistory", "queryable": True},
                {"name": "Orders", "queryable": True},
                {"name": "OrderHistory", "queryable": True},
                {"name": "CustomStream", "queryable": True},
                {"name": "CustomStreamHistory", "queryable": True},
            ]
        }
    )
    filtered_streams = sf_object.get_validated_streams(config=updated_config)
    assert sorted(filtered_streams.keys()) == sorted(predicted_filtered_streams)


def test_discovery_filter(stream_config):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"
    sf_object.describe = Mock(
        return_value={
            "sobjects": [
                {"name": "Account", "queryable": True},
                {"name": "ActivityMetric", "queryable": True},
                {"name": "Leads", "queryable": False},
            ]
        }
    )
    filtered_streams = sf_object.get_validated_streams(config=stream_config)
    assert list(filtered_streams.keys()) == ["Account"]


@pytest.mark.parametrize(
    "sf_types,json_type,with_raise",
    (
        (STRING_TYPES, "string", False),
        (NUMBER_TYPES, "number", False),
        (DATE_TYPES, "string", False),
        (LOOSE_TYPES, "string", False),
        (["fake_type"], None, True),
    ),
)
def test_convert_sf_types(sf_types, json_type, with_raise):
    for sf_type in sf_types:
        if with_raise:
            with pytest.raises(TypeSalesforceException):
                Salesforce.field_to_property_schema({"type": sf_type})
        else:
            assert json_type in Salesforce.field_to_property_schema({"type": sf_type})["type"]
