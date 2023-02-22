#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk"]

TEST_REQUIREMENTS = ["pytest~=6.1", "connector-acceptance-test", "requests-mock==1.9.3", "timeout-decorator==0.5.0"]

setup(
    name="source_tiktok_marketing",
    description="Source implementation for Tiktok Marketing.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={"tests": TEST_REQUIREMENTS},
)
