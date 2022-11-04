#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["requests", "airbyte_ci_common_utils"]

TEST_REQUIREMENTS = ["requests-mock"]

setup(
    version="0.0.0",
    name="airbyte_ci_credentials",
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
            "airbyte_ci_credentials = airbyte_ci_credentials.main:main",
        ],
    },
)
