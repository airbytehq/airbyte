# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any


CASES = [
    ("users", "meta/users", {"id": 11, "employeeId": 1, "lastLogin": "2026-11-01T12:00:00Z", "status": "enabled"}),
    ("time_off_policies", "meta/time_off/policies", {"id": 11, "timeOffTypeId": 2, "effectiveDate": None, "type": "accruing"}),
    (
        "time_off_types",
        "meta/time_off/types",
        {"id": 11, "name": "Vacation", "units": "days", "color": None, "icon": None, "source": "internal"},
    ),
    (
        "employee_time_off_policies",
        "employees/1/time_off/policies",
        {"timeOffPolicyId": 11, "timeOffTypeId": 2, "accrualStartDate": "2026-01-01"},
    ),
    (
        "employee_dependents",
        "employeedependents",
        {"id": "11", "employeeId": "1", "dateOfBirth": "2000-01-01", "maskedSSN": None, "isStudent": None},
    ),
    (
        "training_types",
        "training/type",
        {"id": 11, "name": "Safety", "required": None, "category": [], "linkUrl": None, "renewable": False},
    ),
    ("training_categories", "training/category", {"id": 11, "name": "Safety"}),
    (
        "employee_trainings",
        "training/record/employee/1",
        {
            "id": 11,
            "employeeId": "1",
            "completed": "2026-11-01",
            "credits": "2",
            "hours": None,
            "cost": "50.00 USD",
            "type": "3",
            "instructor": None,
        },
    ),
    (
        "goals",
        "performance/employees/1/goals",
        {
            "id": "11",
            "sharedWithEmployeeIds": [1, 2],
            "milestones": [{"id": 3, "currentValue": None, "lastUpdateUserId": 1}],
            "actions": {"canEditGoalProgressBar": True},
            "lastChangedDateTime": None,
        },
    ),
    (
        "job_openings",
        "applicant_tracking/jobs",
        {"id": 11, "title": {"id": None, "label": "Engineer"}, "postedDate": "2026-11-01T12:00:00Z", "location": None, "hiringLead": None},
    ),
    (
        "job_applications",
        "applicant_tracking/applications",
        {
            "id": 11,
            "appliedDate": "2026-11-01T12:00:00Z",
            "rating": None,
            "applicant": {"id": 7, "firstName": "Example", "avatar": None},
            "job": {"id": 4, "title": {"id": None, "label": "Engineer"}},
        },
    ),
]

SUBSTREAMS = {"employee_time_off_policies", "employee_trainings", "goals"}
KEYED_STREAMS = {"users", "training_types", "training_categories", "employee_trainings"}
ENVELOPES = {
    "time_off_types": "timeOffTypes",
    "employee_dependents": "Employee Dependents",
    "goals": "goals",
    "job_applications": "applications",
}


def payload(stream: str, records: list[dict[str, Any]]) -> dict[str, Any] | list[dict[str, Any]]:
    if stream in KEYED_STREAMS:
        return {str(record["id"]): record for record in records} if records else ([] if stream == "employee_trainings" else {})
    if stream in ENVELOPES:
        result = {ENVELOPES[stream]: records}
        if stream == "job_applications":
            result.update(paginationComplete=True, nextPageUrl=None)
        return result
    return records
