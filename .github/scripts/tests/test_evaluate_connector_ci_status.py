# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


SCRIPT = Path(__file__).parents[1] / "evaluate-connector-ci-status.sh"
BASE_ENV = {
    "GENERATE_MATRIX_RESULT": "success",
    "JVM_CONNECTORS_TEST_RESULT": "success",
    "NON_JVM_CONNECTORS_TEST_RESULT": "success",
    "CONNECTORS_LINT_RESULT": "success",
    "CONNECTOR_QA_CHECKS_RESULT": "success",
    "CONNECTOR_FILES_CHANGED": "true",
    "CONNECTORS_FOUND": "true",
}
BLOCKING_JOB_RESULTS = [
    "GENERATE_MATRIX_RESULT",
    "JVM_CONNECTORS_TEST_RESULT",
    "NON_JVM_CONNECTORS_TEST_RESULT",
    "CONNECTORS_LINT_RESULT",
]


def run_script(**env):
    with TemporaryDirectory() as directory:
        output_file = Path(directory) / "github-output"
        completed = subprocess.run(
            [str(SCRIPT)],
            capture_output=True,
            check=True,
            env={**os.environ, **BASE_ENV, **env, "GITHUB_OUTPUT": str(output_file)},
            text=True,
        )
        completed.output_file_contents = output_file.read_text()
        return completed


def run(**env):
    output = run_script(**env).output_file_contents
    return output.strip().removeprefix("result=")


def test_all_blocking_jobs_success_with_connectors_found():
    assert run() == "success"


def test_qa_failure_fails_summary():
    assert run(CONNECTOR_QA_CHECKS_RESULT="failure") == "failure"


@pytest.mark.parametrize("job_result", BLOCKING_JOB_RESULTS)
def test_other_blocking_job_failure_fails_summary(job_result):
    assert run(**{job_result: "failure"}) == "failure"


@pytest.mark.parametrize("job_result", BLOCKING_JOB_RESULTS + ["CONNECTOR_QA_CHECKS_RESULT"])
@pytest.mark.parametrize("status", ["skipped", "cancelled"])
def test_blocking_job_skipped_or_cancelled_fails_summary(job_result, status):
    assert run(**{job_result: status}) == "failure"


def test_no_op_matrix_on_non_connector_pr_succeeds():
    assert run(CONNECTOR_FILES_CHANGED="false", CONNECTORS_FOUND="false") == "success"


def test_connector_pr_with_empty_matrix_fails():
    assert run(CONNECTOR_FILES_CHANGED="true", CONNECTORS_FOUND="false") == "failure"


def test_workflow_call_with_no_paths_filter_value_succeeds():
    assert run(CONNECTOR_FILES_CHANGED="", CONNECTORS_FOUND="false") == "success"


def test_qa_failure_emits_error_annotation():
    completed = run_script(CONNECTOR_QA_CHECKS_RESULT="failure")
    assert "::error::Job 'connector-qa-checks' reported 'failure', expected 'success'." in completed.stdout
