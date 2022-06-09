#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

# grpcio-status is required by google ads but is not listed in its dependencies.
# this package must be of the same version range that grpcio is.
#
# google-ads 14.1.0 depends on protobuf<3.18.0 and >=3.12.0. Tested every version from 3.18 down until tests passed
# (https://github.com/airbytehq/airbyte/pull/13624)
MAIN_REQUIREMENTS = ["airbyte-cdk~=0.1", "google-ads==14.1.0", "protobuf==3.14", "grpcio-status >= 1.38.1, < 2.0.0", "pendulum"]

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
