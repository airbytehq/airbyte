# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from source_klaviyo.components.campaign_details_transformations import CampaignsDetailedTransformation


def test_transform(requests_mock):
    config = {"api_key": "api_key"}
    transformator = CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    requests_mock.register_uri(
        "GET",
        f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}",
        status_code=200,
        json={"data": {"attributes": {"estimated_recipient_count": 10}}},
        complete_qs=True,
    )
    requests_mock.register_uri(
        "GET",
        input_record["relationships"]["campaign-messages"]["links"]["related"],
        status_code=200,
        json={"data": [{"attributes": {"field": "field"}}]},
        complete_qs=True,
    )

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record


def test_transform_not_campaign_messages(requests_mock):
    config = {"api_key": "api_key"}
    transformator = CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    requests_mock.register_uri(
        "GET",
        f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}",
        status_code=200,
        json={"data": {"attributes": {"estimated_recipient_count": 10}}},
        complete_qs=True,
    )
    requests_mock.register_uri(
        "GET",
        input_record["relationships"]["campaign-messages"]["links"]["related"],
        status_code=200,
        json={},
        complete_qs=True,
    )

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record


def test_transform_not_estimated_recipient_count(requests_mock):
    config = {"api_key": "api_key"}
    transformator = CampaignsDetailedTransformation(config=config)
    input_record = {
        "id": "campaign_id",
        "relationships": {"campaign-messages": {"links": {"related": "https://a.klaviyo.com/api/related_link"}}},
    }

    requests_mock.register_uri(
        "GET",
        f"https://a.klaviyo.com/api/campaign-recipient-estimations/{input_record['id']}",
        status_code=200,
        json={"data": {"attributes": {}}},
        complete_qs=True,
    )
    requests_mock.register_uri(
        "GET",
        input_record["relationships"]["campaign-messages"]["links"]["related"],
        status_code=200,
        json={"data": [{"attributes": {"field": "field"}}]},
        complete_qs=True,
    )

    transformator.transform(input_record)

    assert "campaign_messages" in input_record
    assert "estimated_recipient_count" in input_record
