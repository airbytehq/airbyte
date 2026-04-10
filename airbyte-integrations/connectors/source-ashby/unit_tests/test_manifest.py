# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-ashby manifest.yaml.

Validates that the check stream uses a commonly-permissioned stream (jobs)
rather than one requiring elevated permissions (users).
"""

import pathlib

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def test_check_stream_uses_jobs(manifest):
    """The check block must use the 'jobs' stream, which requires only the common 'Jobs' permission module.

    Previously, the check used the 'users' stream (requiring the 'Organization' permission module),
    causing connection checks to fail for users who only have Jobs/Job Postings permissions.
    See: https://github.com/airbytehq/oncall/issues/11953
    """
    check = manifest.get("check", {})
    stream_names = check.get("stream_names", [])
    assert "jobs" in stream_names, (
        f"Expected 'jobs' in check.stream_names, got {stream_names}. "
        "The check stream should use 'jobs' (Jobs permission module) "
        "instead of 'users' (Organization permission module) to avoid "
        "failing for users with limited API permissions."
    )


def test_check_stream_does_not_use_users(manifest):
    """The check block must NOT use the 'users' stream, which requires the 'Organization' permission module.

    Users who only need jobs/job_postings streams would fail the connection check
    if 'users' is used, since they lack Organization permissions.
    See: https://github.com/airbytehq/oncall/issues/11953
    """
    check = manifest.get("check", {})
    stream_names = check.get("stream_names", [])
    assert "users" not in stream_names, (
        f"'users' should not be in check.stream_names (got {stream_names}). "
        "The 'users' stream requires the 'Organization' permission module, "
        "which many users don't have."
    )


def test_jobs_stream_is_defined(manifest):
    """The 'jobs' stream must be defined in the manifest since it is used for the connection check."""
    streams = manifest.get("definitions", {}).get("streams", {})
    assert "jobs" in streams, "The 'jobs' stream must be defined in the manifest"


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("applications", id="applications"),
        pytest.param("archive_reasons", id="archive_reasons"),
        pytest.param("candidate_tags", id="candidate_tags"),
        pytest.param("candidates", id="candidates"),
        pytest.param("custom_fields", id="custom_fields"),
        pytest.param("departments", id="departments"),
        pytest.param("feedback_form_definitions", id="feedback_form_definitions"),
        pytest.param("interview_schedules", id="interview_schedules"),
        pytest.param("job_postings", id="job_postings"),
        pytest.param("jobs", id="jobs"),
        pytest.param("locations", id="locations"),
        pytest.param("offers", id="offers"),
        pytest.param("sources", id="sources"),
        pytest.param("users", id="users"),
    ],
)
def test_all_streams_use_post_method(manifest, stream_name):
    """All Ashby API streams use POST requests. Verify this convention is maintained."""
    stream = manifest["definitions"]["streams"][stream_name]
    http_method = stream["retriever"]["requester"].get("http_method", "GET")
    assert http_method == "POST", f"Stream '{stream_name}' should use POST method, got {http_method}"
