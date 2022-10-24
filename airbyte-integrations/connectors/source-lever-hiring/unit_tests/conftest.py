#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def test_full_refresh_config():
    return {"base_url": "test_base_url"}


@fixture
def test_incremental_config():
    return {"base_url": "test_base_url", "start_date": "2020-01-01T00:00:00Z"}


@fixture
def test_opportunity_record():
    return {
        "id": "test_id",
        "name": "test_name",
        "contact": "test_contact",
        "headline": "test_headline",
        "stage": "test_stage",
        "confidentiality": "non-confidential",
        "location": "test_location",
        "phones": [{"type": "test_mobile", "value": "test_value"}],
        "emails": ["test_emails"],
        "links": ["test_link_1", "test_link_2"],
        "archived": {"reason": "test_reason", "archivedAt": 1628513942512},
        "tags": [],
        "sources": ["test_source_1"],
        "stageChanges": [{"toStageId": "test_lead-new", "toStageIndex": 0, "updatedAt": 1628509001183, "userId": "test_userId"}],
        "origin": "test_origin",
        "sourcedBy": "test_sourcedBy",
        "owner": "test_owner",
        "followers": ["test_follower"],
        "applications": ["test_application"],
        "createdAt": 1738509001183,
        "updatedAt": 1738542849132,
        "lastInteractionAt": 1738513942512,
        "lastAdvancedAt": 1738513942512,
        "snoozedUntil": None,
        "urls": {"list": "https://hire.sandbox.lever.co/candidates", "show": "https://hire.sandbox.lever.co/candidates/test_show"},
        "isAnonymized": False,
        "dataProtection": None,
    }
