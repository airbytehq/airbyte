# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards the `interviews` stream schema against reintroducing scheduled-interview fields.

`/interview.list` returns interview *definitions*: the reusable interview templates configured
on a job. Its `Interview` component declares exactly the twelve properties asserted here. The
scheduling fields that used to be declared on this stream (`startTime`, `status`, `meetingLink`,
and so on) belong to a *scheduled* interview and were emitted as null on every record; they were
removed in 2.0.0 and the equivalent data lives in the `interview_schedules` stream.

See https://developers.ashbyhq.com/reference/interviewlist.
"""

import logging

from conftest import get_source


_LOGGER = logging.getLogger("airbyte")

_CONFIG = {"api_key": "an-api-key", "start_date": "2026-01-01T00:00:00Z"}

# The `Interview` component of the Ashby OpenAPI definition embedded in the `/interview.list` docs.
_INTERVIEW_LIST_FIELDS = {
    "id",
    "title",
    "externalTitle",
    "type",
    "isArchived",
    "isDebrief",
    "isFeedbackRequired",
    "isFeedbackRequested",
    "instructionsHtml",
    "instructionsPlain",
    "jobId",
    "feedbackFormDefinitionId",
}

# Removed in 2.0.0. Listed explicitly so a regression names the fields rather than a set diff.
_SCHEDULED_INTERVIEW_FIELDS = {
    "applicationId",
    "interviewScheduleId",
    "interviewStageId",
    "status",
    "createdAt",
    "updatedAt",
    "cancelledAt",
    "startTime",
    "endTime",
    "feedbackLink",
    "interviewerUserIds",
    "meetingLink",
}


def _discovered_interviews_properties() -> set:
    catalog = get_source(_CONFIG).discover(_LOGGER, _CONFIG)
    interviews = next(stream for stream in catalog.streams if stream.name == "interviews")
    return set(interviews.json_schema["properties"])


def test_interviews_schema_declares_only_the_fields_interview_list_returns() -> None:
    properties = _discovered_interviews_properties()
    assert properties == _INTERVIEW_LIST_FIELDS


def test_interviews_schema_declares_no_scheduled_interview_fields() -> None:
    declared = sorted(_discovered_interviews_properties() & _SCHEDULED_INTERVIEW_FIELDS)
    assert not declared, f"`interviews` declares scheduling fields `/interview.list` never returns: {declared}"


def test_interview_schedules_still_carries_the_scheduling_fields() -> None:
    """The migration guide points users at `interview_schedules`, so keep that promise tested."""
    catalog = get_source(_CONFIG).discover(_LOGGER, _CONFIG)
    schedules = next(stream for stream in catalog.streams if stream.name == "interview_schedules")
    properties = schedules.json_schema["properties"]
    assert {"applicationId", "interviewStageId", "status", "createdAt", "updatedAt"} <= set(properties)
    event_properties = set(properties["interviewEvents"]["items"]["properties"])
    assert {"startTime", "endTime", "feedbackLink", "interviewerUserIds", "meetingLink", "interviewScheduleId"} <= event_properties
