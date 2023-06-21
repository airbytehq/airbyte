#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "click~=8.1.3",
    "requests",
    "PyYAML~=6.0",
    "GitPython~=3.1.29",
    "pydantic~=1.9",
    "PyGithub~=1.58.0",
    "rich",
]


def local_pkg(name: str) -> str:
    """Returns a path to a local package."""
    return f"{name} @ file://{Path.cwd().parent / name}"


# These internal packages are not yet published to a Pypi repository.
LOCAL_REQUIREMENTS = [local_pkg("ci_credentials")]

TEST_REQUIREMENTS = [
    "pytest~=6.2.5",
    "pytest-mock~=3.10.0",
    "freezegun",
]

DEV_REQUIREMENTS = ["pyinstrument"]
# It is hard to containerize Pandas, it's only used in the QA engine, so I declared it as an extra requires
# TODO update the GHA that install the QA engine to install this extra
QA_ENGINE_REQUIREMENTS = [
    "pandas~=1.5.3",
    "pandas-gbq~=0.19.0",
    "fsspec~=2023.1.0",
    "gcsfs~=2023.1.0",
    "pytablewriter~=0.64.2",
]

PIPELINES_REQUIREMENTS = [
    "dagger-io==0.5.4",
    "asyncer",
    "anyio",
    "more-itertools",
    "docker",
    "requests",
    "semver",
    "airbyte-protocol-models",
    "tabulate",
]

setup(
    version="0.2.1",
    name="ci_connector_ops",
    description="Packaged maintained by the connector operations team to perform CI for connectors",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS + LOCAL_REQUIREMENTS,
    extras_require={
        "tests": QA_ENGINE_REQUIREMENTS + TEST_REQUIREMENTS,
        "dev": QA_ENGINE_REQUIREMENTS + TEST_REQUIREMENTS + DEV_REQUIREMENTS,
        "pipelines": MAIN_REQUIREMENTS + PIPELINES_REQUIREMENTS,
        "qa_engine": MAIN_REQUIREMENTS + QA_ENGINE_REQUIREMENTS,
    },
    # python_requires=">=3.10", TODO upgrade all our CI packages + GHA env to 3.10
    package_data={"ci_connector_ops.qa_engine": ["connector_adoption.sql"]},
    entry_points={
        "console_scripts": [
            "check-test-strictness-level = ci_connector_ops.acceptance_test_config_checks:check_test_strictness_level",
            "write-review-requirements-file = ci_connector_ops.acceptance_test_config_checks:write_review_requirements_file",
            "print-mandatory-reviewers = ci_connector_ops.acceptance_test_config_checks:print_mandatory_reviewers",
            "allowed-hosts-checks = ci_connector_ops.allowed_hosts_checks:check_allowed_hosts",
            "run-qa-checks = ci_connector_ops.qa_checks:run_qa_checks",
            "airbyte-ci = ci_connector_ops.pipelines.commands.airbyte_ci:airbyte_ci",
        ],
    },
)
