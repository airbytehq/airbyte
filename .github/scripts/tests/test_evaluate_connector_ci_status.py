# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import yaml


REPO_ROOT = Path(__file__).parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "connector-ci-checks.yml"
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
DETECT_CDK_PRERELEASE_SCRIPT = step("cdk-prerelease-check", "detect-cdk-prerelease")["run"]
EVALUATE_CDK_PRERELEASE_SCRIPT = step("cdk-prerelease-check", "evaluate-cdk-prerelease")["run"]
# Jobs evaluated by the 'Evaluate Status' loop, for example "connector-qa-checks".
EVALUATED_JOBS = re.findall(r'"([a-z-]+)=\$\{[A-Z_]+_RESULT:-\}"', EVALUATE_STATUS_SCRIPT)


def run_bash(script: str, env: dict, check: bool = True, cwd: Path | None = None):
    """Run a 'run' block the way GitHub Actions does by default ('bash -e {0}')."""
    with TemporaryDirectory() as directory:
        output_file = Path(directory) / "github-output"
        output_file.touch()
        completed = subprocess.run(
            ["bash", "-e", "-c", script],
            capture_output=True,
            check=check,
            cwd=cwd,
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


def test_connector_files_changed_is_false_outside_pull_requests():
    # On the workflow_call path, paths-filter diffs against its own git base, so the
    # empty-matrix guard only applies to pull_request events.
    assert JOBS["generate-matrix"]["outputs"]["connector-files-changed"] == (
        "${{ github.event_name == 'pull_request' && steps.cdk-changes.outputs.connectors || 'false' }}"
    )


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


# 'poe' stub for 'Detect Python CDK Prerelease Pin'. 'get-language' answers from
# $CONNECTOR_LANGUAGE, and 'detect-cdk-info' runs the real poe-tasks script against the
# pyproject.toml in the working directory, like the 'detect-cdk-info' poe task does.
POE_STUB = f"""#!/usr/bin/env bash
case "$*" in
  "-qq get-language") echo "${{CONNECTOR_LANGUAGE}}" ;;
  "-qq detect-cdk-info") exec "{sys.executable}" "{REPO_ROOT / "poe-tasks" / "detect-python-cdk.py"}" ;;
  *) echo "unexpected poe arguments: $*" >&2; exit 2 ;;
esac
"""


def detect_cdk_prerelease(pyproject: str | None, language: str = "python"):
    with TemporaryDirectory() as directory:
        bin_dir = Path(directory) / "bin"
        bin_dir.mkdir()
        poe = bin_dir / "poe"
        poe.write_text(POE_STUB)
        poe.chmod(0o755)
        connector_dir = Path(directory) / "source-example"
        connector_dir.mkdir()
        if pyproject is not None:
            (connector_dir / "pyproject.toml").write_text(pyproject)
        completed, output = run_bash(
            DETECT_CDK_PRERELEASE_SCRIPT,
            {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "CONNECTOR_LANGUAGE": language},
            cwd=connector_dir,
        )
        return completed, output.strip()


def cdk_pyproject(dependency: str) -> str:
    return f'[tool.poetry.dependencies]\npython = "^3.10"\nairbyte-cdk = {dependency}\n'


@pytest.mark.parametrize(
    "dependency, pinned",
    [
        ('"^7.0.0"', False),
        ('{ version = "^7.0.0", extras = ["sql"] }', False),
        ('">=6.61.6,<8.0"', False),
        ('"7.1.0.dev2"', True),
        ('"7.1.0rc1"', True),
        ('{ git = "https://github.com/airbytehq/airbyte-python-cdk.git", branch = "main" }', True),
        ('{ path = "../../../../airbyte-python-cdk", develop = true }', True),
        ('"*"', True),
        ('{ extras = ["sql"] }', True),
        ('"latest"', True),
    ],
    ids=["caret", "caret-with-extras", "range", "dev", "rc", "git-ref", "local-path", "wildcard", "unknown-type", "unparsable"],
)
def test_detect_cdk_prerelease_pin(dependency, pinned):
    _, output = detect_cdk_prerelease(cdk_pyproject(dependency))
    assert output == f"pinned={str(pinned).lower()}"


@pytest.mark.parametrize(
    "pyproject",
    [None, '[tool.poetry.dependencies]\npython = "^3.10"\n', "not = [valid toml"],
    ids=["missing-pyproject", "no-cdk-dependency", "unparsable-pyproject"],
)
def test_detect_cdk_prerelease_skips_on_error(pyproject):
    completed, output = detect_cdk_prerelease(pyproject)
    assert output == "pinned=false"
    assert "Skipping CDK prerelease check: " in completed.stdout


@pytest.mark.parametrize("language", ["java", "manifest-only"])
def test_detect_cdk_prerelease_skips_non_python_connectors(language):
    # The pyproject.toml would count as a pin if it were read.
    completed, output = detect_cdk_prerelease(cdk_pyproject('"*"'), language=language)
    assert output == "pinned=false"
    assert "Skipping CDK prerelease check for non-Python connector." in completed.stdout


def test_detect_cdk_prerelease_script_does_not_interpolate_expressions():
    assert "${{" not in DETECT_CDK_PRERELEASE_SCRIPT


# --- 'connectors' path filter of 'Detect Changed Paths' ---

PATHS_FILTER_STEP = step("generate-matrix", "cdk-changes")
CONNECTORS_FILTER = yaml.safe_load(PATHS_FILTER_STEP["with"]["filters"])["connectors"]
GET_MODIFIED_CONNECTORS = (REPO_ROOT / "poe-tasks" / "get-modified-connectors.sh").read_text()


def glob_to_regex(pattern: str) -> re.Pattern:
    """Translate the globs used by the filter, with picomatch's '{dot: true}' semantics."""
    regex, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex, i = regex + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            regex, i = regex + ".*", i + 2
        elif pattern[i] == "*":
            regex, i = regex + "[^/]*", i + 1
        elif pattern[i] in "?[]{}()!+@":
            raise ValueError(f"Unsupported glob syntax in {pattern!r}; extend glob_to_regex.")
        else:
            regex, i = regex + re.escape(pattern[i]), i + 1
    return re.compile(regex + r"\Z")


def connectors_filter_matches(filename: str, status: str) -> bool:
    """dorny/paths-filter 'some-with-excludes': a file matches when a rule whose change
    status applies includes it, and no such rule excludes it."""
    included = False
    for rule in CONNECTORS_FILTER:
        statuses, pattern = (None, rule) if isinstance(rule, str) else next(iter(rule.items()))
        if statuses is not None and status not in statuses.split("|"):
            continue
        if pattern.startswith("!"):
            if glob_to_regex(pattern[1:]).match(filename):
                return False
        elif glob_to_regex(pattern).match(filename):
            included = True
    return included


def script_returns_connector(filename: str) -> bool:
    """The ignore and connector-path rules of poe-tasks/get-modified-connectors.sh."""
    patterns_block = re.search(r"^ignore_patterns=\((.*?)^\)", GET_MODIFIED_CONNECTORS, re.M | re.S).group(1)
    ignore = "(" + "|".join(re.findall(r"'([^']*)'", patterns_block)) + ")$"
    connector_path = re.search(r"grep -E '(\^airbyte-integrations/connectors/[^']*)'", GET_MODIFIED_CONNECTORS).group(1)
    return not re.search(f"(/{ignore}|^{ignore})", filename) and bool(re.search(connector_path, filename))


CONNECTORS_FILTER_CASES = [
    ("airbyte-integrations/connectors/source-example/manifest.yaml", True),
    ("airbyte-integrations/connectors/source-example/metadata.yaml", True),
    ("airbyte-integrations/connectors/destination-example/src/main/kotlin/Example.kt", True),
    ("airbyte-integrations/connectors/source-example/.dockerignore", True),
    ("airbyte-integrations/connectors/source-example/docs/README.md", True),
    ("airbyte-integrations/connectors/source-example/poe_tasks.toml", False),
    ("airbyte-integrations/connectors/source-example/unit_tests/poe_tasks.toml", False),
    ("airbyte-integrations/connectors/source-example/.coveragerc", False),
    ("airbyte-integrations/connectors/source-example/README.md", False),
    ("airbyte-integrations/connectors/destination-example/CONTRIBUTING.md", False),
    ("airbyte-integrations/connectors/README.md", False),
    ("airbyte-integrations/connector-templates/source-example/manifest.yaml", False),
    ("docs/integrations/sources/example.md", False),
    ("poe_tasks.toml", False),
]


@pytest.mark.parametrize("filename, expected", CONNECTORS_FILTER_CASES)
@pytest.mark.parametrize("status", ["added", "modified"])
def test_connectors_filter(filename, expected, status):
    assert connectors_filter_matches(filename, status) == expected


@pytest.mark.parametrize("filename, _", CONNECTORS_FILTER_CASES)
def test_connectors_filter_mirrors_get_modified_connectors(filename, _):
    assert connectors_filter_matches(filename, "modified") == script_returns_connector(filename)


def test_connectors_filter_ignores_removed_files():
    # The script skips a connector whose directory was removed, so it returns no connector.
    assert not connectors_filter_matches("airbyte-integrations/connectors/source-example/manifest.yaml", "removed")


def test_connectors_filter_uses_some_with_excludes():
    # With the default 'some' quantifier, every negated pattern matches all other files.
    assert PATHS_FILTER_STEP["with"]["predicate-quantifier"] == "some-with-excludes"
