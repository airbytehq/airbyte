# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for the Zoom Revenue Accelerator (ZRA) streams in source-zoom.

These tests mock the Zoom API responses and verify that the 5 new ZRA streams
correctly fetch, paginate, and extract records from the API.
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "authorization_endpoint": "https://zoom.us/oauth/token",
}

_OAUTH_TOKEN_RESPONSE = {
    "access_token": "test_access_token",
    "token_type": "bearer",
    "expires_in": 3600,
}

_CONVERSATIONS_PAGE_1 = {
    "next_page_token": "page2token",
    "page_size": 30,
    "conversations": [
        {
            "conversation_id": "conv-001",
            "host_id": "user-abc",
            "meeting_id": 123456789,
            "meeting_uuid": "abc123==",
            "deal_id": "deal-001",
            "conversation_topic": "Sales Call",
            "duration": 45,
            "conversation_type": "meeting",
            "meeting_start_time": "2024-01-15T10:00:00Z",
            "iq_processed_time": "2024-01-15T11:00:00Z",
            "engagement_score": 75,
            "sentiment_score": 80,
            "engaging_questions_count": 5,
            "next_steps_count": 3,
            "filler_words_count": 2,
            "processing_analysis": False,
            "topic": "Sales Call",
        },
    ],
}

_CONVERSATIONS_PAGE_2 = {
    "next_page_token": "",
    "page_size": 30,
    "conversations": [
        {
            "conversation_id": "conv-002",
            "host_id": "user-xyz",
            "meeting_id": 987654321,
            "meeting_uuid": "xyz789==",
            "deal_id": "deal-002",
            "conversation_topic": "Demo Call",
            "duration": 30,
            "conversation_type": "phone",
            "meeting_start_time": "2024-01-16T14:00:00Z",
            "iq_processed_time": "2024-01-16T15:00:00Z",
            "engagement_score": 60,
            "sentiment_score": 70,
            "engaging_questions_count": 3,
            "next_steps_count": 1,
            "filler_words_count": 4,
            "processing_analysis": False,
            "topic": "Demo Call",
        },
    ],
}

_CONVERSATION_DETAIL = {
    "conversation_id": "conv-001",
    "meeting_id": 123456789,
    "meeting_uuid": "abc123==",
    "host_id": "user-abc",
    "host_email": "host@example.com",
    "conversation_topic": "Sales Call",
    "duration": 45,
    "summary": "Discussed pricing and next steps.",
    "conversation_type": "meeting",
    "stage_during_conversation": "Negotiation",
    "meeting_start_time": "2024-01-15T10:00:00Z",
    "iq_processed_time": "2024-01-15T11:00:00Z",
    "engagement_score": 75,
    "sentiment_score": 80,
    "conversation_url": "https://zoom.us/iq/conversation?meetingId=abc123",
    "deal": {
        "id": "deal-001",
        "name": "Enterprise Deal",
        "stage": "Negotiation",
        "customer_crm_account_name": "ACME Corp",
        "close_date": "2024-03-01",
    },
    "participants": [
        {"display_name": "Alice", "email": "alice@example.com", "type": "rep"},
        {"display_name": "Bob", "email": "bob@customer.com", "type": "customer"},
    ],
}

_INTERACTIONS_RESPONSE = {
    "next_page_token": "",
    "page_size": 30,
    "participants": [
        {
            "user_id": "user-abc",
            "display_name": "Alice",
            "email": "alice@example.com",
            "speaker_type": "rep",
            "transcripts": [
                {
                    "item_id": "0",
                    "text": "Hello, welcome to the call.",
                    "start_time": "2024-01-15T10:00:00Z",
                    "end_time": "2024-01-15T10:00:05Z",
                },
            ],
            "metrics": {
                "talk_to_listen_ratio": 0.6,
                "longest_monolog": 120,
                "talk_speed": 140,
                "filler_words": 2,
                "patience": 5,
            },
        },
    ],
}

_CONTENT_ANALYSIS_RESPONSE = {
    "summary": "A productive sales call discussing pricing.",
    "smart_chapters": [
        {
            "title": "Introduction",
            "summary": "Greetings and agenda setting.",
            "category": "opening",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T10:05:00Z",
        },
    ],
    "next_steps": [
        {
            "section": [
                {
                    "user_id": "user-abc",
                    "display_name": "Alice",
                    "text": "Send proposal by Friday",
                    "utterance": "I will send the proposal by Friday",
                    "label": "next_step",
                    "start_time": "2024-01-15T10:40:00Z",
                    "end_time": "2024-01-15T10:40:10Z",
                },
            ],
        },
    ],
}

_SCORECARDS_RESPONSE = {
    "next_page_token": "",
    "page_size": 30,
    "scorecards": [
        {
            "scorecard_id": "sc-001",
            "scorecard_name": "Sales Quality",
            "scorecard_description": "Rate the quality of the sales call",
            "average_score": 8.5,
            "rate_time": "2024-01-16T09:00:00Z",
            "rater": {
                "email": "manager@example.com",
                "display_name": "Manager",
                "user_id": "user-mgr",
            },
            "scorecard_questions": [
                {
                    "question_id": "q-001",
                    "question_title": "Discovery Quality",
                    "score": 9,
                    "question_description": "How well did the rep discover needs?",
                    "question_comment": "Excellent discovery.",
                    "scale": {
                        "min_score_label": "Poor",
                        "max_score_label": "Excellent",
                    },
                    "justification": "Asked probing questions throughout.",
                    "answer": "Excellent",
                },
            ],
        },
    ],
}


def _register_oauth_mock(m):
    m.post("https://zoom.us/oauth/token", json=_OAUTH_TOKEN_RESPONSE)


def _register_conversations_mock(m):
    m.get(
        "https://api.zoom.us/v2/zra/conversations",
        [
            {"json": _CONVERSATIONS_PAGE_1},
            {"json": _CONVERSATIONS_PAGE_2},
        ],
    )


def _sync(stream_name: str):
    source = get_source(config=_CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, _CONFIG, catalog)


def test_zra_conversations_paginates_and_returns_records():
    with requests_mock.Mocker() as m:
        _register_oauth_mock(m)
        _register_conversations_mock(m)

        output = _sync("zra_conversations")

        assert not output.errors, f"Unexpected errors: {output.errors}"
        records = output.records
        assert len(records) == 2
        assert records[0].record.data["conversation_id"] == "conv-001"
        assert records[0].record.data["engagement_score"] == 75
        assert records[1].record.data["conversation_id"] == "conv-002"
        assert records[1].record.data["conversation_type"] == "phone"


def test_zra_conversation_details_fetches_child_records():
    with requests_mock.Mocker() as m:
        _register_oauth_mock(m)
        _register_conversations_mock(m)
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-001",
            json=_CONVERSATION_DETAIL,
        )
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-002",
            json={**_CONVERSATION_DETAIL, "conversation_id": "conv-002"},
        )

        output = _sync("zra_conversation_details")

        assert not output.errors, f"Unexpected errors: {output.errors}"
        records = output.records
        assert len(records) == 2
        assert records[0].record.data["conversation_id"] == "conv-001"
        assert records[0].record.data["host_email"] == "host@example.com"
        assert records[0].record.data["summary"] == "Discussed pricing and next steps."


def test_zra_conversation_interactions_fetches_participants():
    with requests_mock.Mocker() as m:
        _register_oauth_mock(m)
        _register_conversations_mock(m)
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-001/interactions",
            json=_INTERACTIONS_RESPONSE,
        )
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-002/interactions",
            json=_INTERACTIONS_RESPONSE,
        )

        output = _sync("zra_conversation_interactions")

        assert not output.errors, f"Unexpected errors: {output.errors}"
        records = output.records
        assert len(records) == 2
        assert records[0].record.data["conversation_id"] == "conv-001"
        assert records[0].record.data["display_name"] == "Alice"
        assert records[0].record.data["speaker_type"] == "rep"
        assert records[0].record.data["metrics"]["talk_to_listen_ratio"] == 0.6


def test_zra_conversation_content_analysis_fetches_analysis():
    with requests_mock.Mocker() as m:
        _register_oauth_mock(m)
        _register_conversations_mock(m)
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-001/content_analysis",
            json=_CONTENT_ANALYSIS_RESPONSE,
        )
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-002/content_analysis",
            json=_CONTENT_ANALYSIS_RESPONSE,
        )

        output = _sync("zra_conversation_content_analysis")

        assert not output.errors, f"Unexpected errors: {output.errors}"
        records = output.records
        assert len(records) == 2
        assert records[0].record.data["conversation_id"] == "conv-001"
        assert records[0].record.data["summary"] == "A productive sales call discussing pricing."
        assert len(records[0].record.data["smart_chapters"]) == 1


def test_zra_conversation_scorecards_fetches_scorecards():
    with requests_mock.Mocker() as m:
        _register_oauth_mock(m)
        _register_conversations_mock(m)
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-001/scorecards",
            json=_SCORECARDS_RESPONSE,
        )
        m.get(
            "https://api.zoom.us/v2/zra/conversations/conv-002/scorecards",
            json=_SCORECARDS_RESPONSE,
        )

        output = _sync("zra_conversation_scorecards")

        assert not output.errors, f"Unexpected errors: {output.errors}"
        records = output.records
        assert len(records) == 2
        assert records[0].record.data["conversation_id"] == "conv-001"
        assert records[0].record.data["scorecard_id"] == "sc-001"
        assert records[0].record.data["average_score"] == 8.5
        assert records[0].record.data["rater"]["display_name"] == "Manager"
