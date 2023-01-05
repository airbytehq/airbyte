#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "pendulum~=2.1.2", "sgqlc"]

TEST_REQUIREMENTS = ["pytest~=6.1", "source-acceptance-test", "responses~=0.19.0"]

setup(
    name="source_github",
    description="Source implementation for Github.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
