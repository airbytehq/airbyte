#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "requests",
    "ci_common_utils",
    "unidiff",
    "mdutils~=1.3.1",
    "mypy==0.930",
]

TEST_REQUIREMENTS = ["requests-mock", "pytest", "black", "lxml", "isort"]

setup(
    version="0.0.0",
    name="ci_code_validator",
    description="Load and extract CI secrets for test suites",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    python_requires=">=3.9",
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "ci_sonar_qube = ci_sonar_qube.main:main",
            "ci_changes_detection = ci_changes_detection.main:main",
        ],
    },
)
