#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="source_slack",
    description="Source implementation for Slack.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-cdk @ git+https://git@github.com/airbytehq/airbyte.git@grubberr/17919-airbyte_cdk#egg=airbyte_cdk&subdirectory=airbyte-cdk/python", "pendulum>=2,<3"],
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
