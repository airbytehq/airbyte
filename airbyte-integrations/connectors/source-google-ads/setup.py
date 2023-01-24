#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

# pin protobuf==3.20.0 as other versions may cause problems on different architectures
# (see https://github.com/airbytehq/airbyte/issues/13580)
MAIN_REQUIREMENTS = ["airbyte-cdk>=0.2.2", "google-ads==19.0.0", "protobuf", "pendulum"]

TEST_REQUIREMENTS = ["pytest~=6.1", "pytest-mock", "freezegun", "requests-mock"]

setup(
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
