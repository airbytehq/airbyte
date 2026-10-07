# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml


WORKFLOW = Path(__file__).parents[3] / ".github" / "workflows" / "connector-ci-checks.yml"
JOBS = yaml.safe_load(WORKFLOW.read_text())["jobs"]
BASE_ENV = {
    "GENERATE_MATRIX_RESULT": "success",
    "JVM_CONNECTORS_TEST_RESULT": "success",
    "NON_JVM_CONNECTORS_TEST_RESULT": "success",
    "CONNECTORS_LINT_RESULT": "success",
    "CONNECTOR_QA_CHECKS_RESULT": "success",
    "CDK_PRERELEASE_CHECK_RESULT": "success",
    "CONNECTOR_FILES_CHANGED": "true",
    "CONNECTORS_FOUND": "true",
}
BLOCKING_JOB_RESULTS = [
    "GENERATE_MATRIX_RESULT",
    "JVM_CONNECTORS_TEST_RESULT",
    "NON_JVM_CONNECTORS_TEST_RESULT",
    "CONNECTORS_LINT_RESULT",
    "CDK_PRERELEASE_CHECK_RESULT",
]


def step(job: str, step_id: str) -> dict:
    return next(step for step in JOBS[job]["steps"] if step.get("id") == step_id)


EVALUATE_STATUS_STEP = step("connector-ci-checks-summary", "evaluate-status")
EVALUATE_STATUS_SCRIPT = EVALUATE_STATUS_STEP["run"]
EVALUATE_CDK_PRERELEASE_SCRIPT = step("cdk-prerelease-check", "evaluate-cdk-prerelease")["run"]
# Jobs evaluated by the 'Evaluate Status' loop, for example "connector-qa-checks".
EVALUATED_JOBS = re.findall(r'"([a-z-]+)=\$\{[A-Z_]+_RESULT:-\}"', EVALUATE_STATUS_SCRIPT)


def run_bash(script: str, env: dict, check: bool = True):
    """Run a 'run' block the way GitHub Actions does by default ('bash -e {0}')."""
    with TemporaryDirectory() as directory:
        output_file = Path(directory) / "github-output"
        output_file.touch()
        completed = subprocess.run(
            ["bash", "-e", "-c", script],
            capture_output=True,
            check=check,
            env={**os.environ, **env, "GITHUB_OUTPUT": str(output_file)},
            text=True,
        )
        return completed, output_file.read_text()


def run_script(**env):
    return run_bash(EVALUATE_STATUS_SCRIPT, {**BASE_ENV, **env})


def run(**env):
    _, output = run_script(**env)
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
    completed, _ = run_script(CONNECTOR_QA_CHECKS_RESULT="failure")
    assert "::error::Job 'connector-qa-checks' reported 'failure', expected 'success'." in completed.stdout


def test_evaluate_status_script_does_not_interpolate_expressions():
    assert "${{" not in EVALUATE_STATUS_SCRIPT


def test_summary_evaluates_every_job_it_needs():
    # A job in 'needs' but not in the loop is silently ignored, and a job in the
    # loop but not in 'needs' always reports an empty result.
    assert sorted(EVALUATED_JOBS) == sorted(JOBS["connector-ci-checks-summary"]["needs"])


@pytest.mark.parametrize("job", EVALUATED_JOBS)
def test_evaluated_job_result_comes_from_its_own_needs_entry(job):
    variable = re.search(rf'"{job}=\$\{{([A-Z_]+):-\}}"', EVALUATE_STATUS_SCRIPT).group(1)
    assert EVALUATE_STATUS_STEP["env"][variable] == f"${{{{ needs.{job}.result }}}}"


@pytest.mark.parametrize("job", EVALUATED_JOBS)
def test_evaluated_job_is_not_skipped_for_drafts_or_allowed_to_fail(job):
    # A draft guard reports 'skipped', which fails the summary of every draft run, and a
    # job-level 'continue-on-error' reports 'success' for a job whose checks failed.
    assert "draft" not in str(JOBS[job].get("if", ""))
    assert "continue-on-error" not in JOBS[job]


CDK_PRERELEASE_ENV = {
    "CONNECTOR": "source-example",
    "BASE_VERSION": "1.2.3",
    "HEAD_VERSION": "1.2.4",
    "PROGRESSIVE_ROLLOUT": "false",
}


def run_cdk_prerelease_check(**env):
    completed, _ = run_bash(EVALUATE_CDK_PRERELEASE_SCRIPT, {**CDK_PRERELEASE_ENV, **env}, check=False)
    return completed


def test_cdk_prerelease_pin_with_unchanged_version_warns():
    completed = run_cdk_prerelease_check(HEAD_VERSION="1.2.3")
    assert completed.returncode == 0
    assert completed.stdout.startswith(
        "::warning file=airbyte-integrations/connectors/source-example/pyproject.toml,title=Python CDK prerelease pin::"
    )
    assert "does not publish it" in completed.stdout


def test_cdk_prerelease_pin_with_progressive_rollout_warns():
    completed = run_cdk_prerelease_check(PROGRESSIVE_ROLLOUT="true")
    assert completed.returncode == 0
    assert completed.stdout.startswith("::warning ")
    assert "progressive rollout" in completed.stdout


@pytest.mark.parametrize("base_version", ["1.2.3", ""], ids=["version-bump", "new-connector"])
def test_cdk_prerelease_pin_published_to_every_connection_fails(base_version):
    completed = run_cdk_prerelease_check(BASE_VERSION=base_version)
    assert completed.returncode == 1
    assert completed.stdout.startswith(
        "::error file=airbyte-integrations/connectors/source-example/pyproject.toml,title=Python CDK prerelease pin::"
    )
    assert "every connection at once" in completed.stdout


def test_cdk_prerelease_pin_with_progressive_rollout_unset_fails():
    # 'Read Release Settings' reads an unset flag as 'false', like publish_connectors.yml.
    assert run_cdk_prerelease_check(PROGRESSIVE_ROLLOUT="").returncode == 1


def test_cdk_prerelease_script_does_not_interpolate_expressions():
    assert "${{" not in EVALUATE_CDK_PRERELEASE_SCRIPT
