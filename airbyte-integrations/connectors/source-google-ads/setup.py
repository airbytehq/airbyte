#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

# pin protobuf==3.20.0 as other versions may cause problems on different architectures
# (see https://github.com/airbytehq/airbyte/issues/13580)
# pendulum <3.0.0 is required to align with the CDK version, and should be updated once the next issue is resolved:
# https://github.com/airbytehq/airbyte/issues/33573
MAIN_REQUIREMENTS = ["airbyte-cdk>=0.51.3", "google-ads==22.1.0", "protobuf", "pendulum<3.0.0"]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock", "freezegun", "requests-mock"]

setup(
    entry_points={
        "console_scripts": [
            "source-google-ads=source_google_ads.run:run",
        ],
    },
    name="source_google_ads",
    description="Source implementation for Google Ads.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
