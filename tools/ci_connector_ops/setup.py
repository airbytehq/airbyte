#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "requests",
    "PyYAML~=6.0",
    "GitPython~=3.1.29",
    "pandas~=1.5.3",
    "pandas-gbq~=0.19.0",
    "pydantic~=1.10.4",
    "fsspec~=2023.1.0",
    "gcsfs~=2023.1.0"
]

TEST_REQUIREMENTS = [
    "pytest~=6.2.5",
    "pytest-mock~=3.10.0",
]

setup(
    version="0.1.10",
    name="ci_connector_ops",
    description="Packaged maintained by the connector operations team to perform CI for connectors",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    python_requires=">=3.9",
    package_data={"ci_connector_ops.qa_engine": ["connector_adoption.sql"]},
    entry_points={
        "console_scripts": [
            "check-test-strictness-level = ci_connector_ops.sat_config_checks:check_test_strictness_level",
            "write-review-requirements-file = ci_connector_ops.sat_config_checks:write_review_requirements_file",
            "print-mandatory-reviewers = ci_connector_ops.sat_config_checks:print_mandatory_reviewers",
            "allowed-hosts-checks = ci_connector_ops.allowed_hosts_checks:check_allowed_hosts",
            "run-qa-engine = ci_connector_ops.qa_engine.main:main",
            "run-qa-checks = ci_connector_ops.qa_checks:run_qa_checks"
        ],
    },
)
