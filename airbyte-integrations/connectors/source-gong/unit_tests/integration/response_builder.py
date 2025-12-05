#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from http import HTTPStatus
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse

from .config import (
    ANSWERED_SCORECARD_ID,
    CALL_ID,
    FOLDER_ID,
    SCORECARD_ID,
    TRACKER_ID,
    USER_ID,
    WORKSPACE_ID,
)


def build_response(
    body: Union[Mapping[str, Any], List[Mapping[str, Any]]],
    status_code: HTTPStatus = HTTPStatus.OK,
    headers: Optional[Mapping[str, str]] = None,
) -> HttpResponse:
    headers = headers or {}
    return HttpResponse(body=json.dumps(body), status_code=status_code.value, headers=headers)


def workspaces_response(
    workspace_id: str = WORKSPACE_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "workspaces": [
            {
                "id": workspace_id,
                "name": "Test Workspace",
                "description": "Test workspace description",
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def call_transcripts_response(
    call_id: str = CALL_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "callTranscripts": [
            {
                "callId": call_id,
                "transcript": [
                    {
                        "speakerId": "speaker_1",
                        "topic": "Introduction",
                        "sentences": [
                            {
                                "start": 0,
                                "end": 5000,
                                "text": "Hello, this is a test transcript.",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def trackers_response(
    tracker_id: str = TRACKER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "trackers": [
            {
                "trackerId": tracker_id,
                "name": "Test Tracker",
                "type": "KEYWORD",
                "keywords": ["test", "keyword"],
                "enabled": True,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def library_folders_response(
    folder_id: str = FOLDER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "folders": [
            {
                "id": folder_id,
                "name": "Test Folder",
                "creatorUserId": USER_ID,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def library_folder_content_response(
    call_id: str = CALL_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "calls": [
            {
                "id": call_id,
                "title": "Test Call",
                "started": "2024-01-15T10:00:00.000Z",
                "duration": 3600,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_activity_aggregate_response(
    user_id: str = USER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "usersAggregateActivityStats": [
            {
                "userId": user_id,
                "callsAsHost": 10,
                "callsAttended": 25,
                "callsGaveComments": 5,
                "callsReceivedComments": 8,
                "callsAccessedRecording": 15,
                "callsMarkedAsFeedbackGiven": 3,
                "callsMarkedAsFeedbackReceived": 4,
                "callsScorecardsFilled": 2,
                "callsScorecardsReceived": 3,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_activity_day_by_day_response(
    user_id: str = USER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "usersDetailedActivities": [
            {
                "userId": user_id,
                "dailyActivityStats": [
                    {
                        "date": "2024-01-15",
                        "callsAsHost": 2,
                        "callsAttended": 5,
                        "callsGaveComments": 1,
                        "callsReceivedComments": 2,
                    }
                ],
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def stats_interaction_response(
    user_id: str = USER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "peopleInteractionStats": [
            {
                "personId": user_id,
                "name": "Test User",
                "emailAddress": "test@example.com",
                "callsCount": 15,
                "unscheduledCallsCount": 3,
                "scheduledCallsCount": 12,
                "totalDuration": 54000,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def users_response(
    user_id: str = USER_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "users": [
            {
                "id": user_id,
                "emailAddress": "test@example.com",
                "firstName": "Test",
                "lastName": "User",
                "title": "Engineer",
                "active": True,
                "created": "2024-01-01T00:00:00.000Z",
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def calls_response(
    call_id: str = CALL_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "calls": [
            {
                "id": call_id,
                "url": "https://app.gong.io/call?id=" + call_id,
                "title": "Test Call",
                "scheduled": "2024-01-15T10:00:00.000Z",
                "started": "2024-01-15T10:00:00.000Z",
                "duration": 3600,
                "primaryUserId": USER_ID,
                "direction": "Inbound",
                "system": "Zoom",
                "scope": "External",
                "media": "Video",
                "language": "en-US",
                "workspaceId": WORKSPACE_ID,
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def extensive_calls_response(
    call_id: str = CALL_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "calls": [
            {
                "metaData": {
                    "id": call_id,
                    "url": "https://app.gong.io/call?id=" + call_id,
                    "title": "Test Extensive Call",
                    "scheduled": "2024-01-15T10:00:00.000Z",
                    "started": "2024-01-15T10:00:00.000Z",
                    "duration": 3600,
                    "primaryUserId": USER_ID,
                    "direction": "Inbound",
                    "system": "Zoom",
                    "scope": "External",
                    "media": "Video",
                    "language": "en-US",
                    "workspaceId": WORKSPACE_ID,
                },
                "parties": [
                    {
                        "id": "party_1",
                        "emailAddress": "test@example.com",
                        "name": "Test User",
                        "title": "Engineer",
                        "userId": USER_ID,
                        "speakerId": "speaker_1",
                        "context": [],
                        "affiliation": "Internal",
                    }
                ],
                "content": {
                    "topics": [{"name": "Introduction", "duration": 300}],
                    "trackers": [],
                    "highlights": [],
                },
                "interaction": {
                    "speakers": [{"speakerId": "speaker_1", "talkTime": 1800}],
                    "questions": {"companyCount": 5, "nonCompanyCount": 3},
                },
                "collaboration": {"publicComments": []},
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def scorecards_response(
    scorecard_id: str = SCORECARD_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "scorecards": [
            {
                "scorecardId": scorecard_id,
                "scorecardName": "Test Scorecard",
                "enabled": True,
                "updatedAt": "2024-01-15T10:00:00.000Z",
                "questions": [
                    {
                        "questionId": "question_1",
                        "questionRevisionId": "revision_1",
                        "questionText": "How was the call quality?",
                        "isOverall": False,
                    }
                ],
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def answered_scorecards_response(
    answered_scorecard_id: str = ANSWERED_SCORECARD_ID,
    has_next: bool = False,
    cursor: Optional[str] = None,
) -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        "answeredScorecards": [
            {
                "answeredScorecardId": answered_scorecard_id,
                "scorecardId": SCORECARD_ID,
                "scorecardName": "Test Scorecard",
                "callId": CALL_ID,
                "callStartTime": "2024-01-15T10:00:00.000Z",
                "reviewedUserId": USER_ID,
                "reviewerUserId": USER_ID,
                "reviewTime": "2024-01-15T11:00:00.000Z",
                "visibilityType": "Public",
                "answers": [
                    {
                        "questionId": "question_1",
                        "questionRevisionId": "revision_1",
                        "isOverall": False,
                        "answerText": "Good",
                    }
                ],
            }
        ],
    }
    if has_next and cursor:
        body["records"] = {"cursor": cursor}
    return build_response(body=body, status_code=HTTPStatus.OK)


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    error_messages = {
        HTTPStatus.UNAUTHORIZED: {"requestId": "test_request_id", "errors": [{"message": "Unauthorized"}]},
        HTTPStatus.FORBIDDEN: {"requestId": "test_request_id", "errors": [{"message": "Forbidden"}]},
        HTTPStatus.TOO_MANY_REQUESTS: {"requestId": "test_request_id", "errors": [{"message": "Rate limit exceeded"}]},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"requestId": "test_request_id", "errors": [{"message": "Internal server error"}]},
    }
    body = error_messages.get(status_code, {"requestId": "test_request_id", "errors": [{"message": "Unknown error"}]})
    return build_response(body=body, status_code=status_code)


def empty_response(stream_key: str = "workspaces") -> HttpResponse:
    body = {
        "requestId": "test_request_id",
        stream_key: [],
    }
    return build_response(body=body, status_code=HTTPStatus.OK)
