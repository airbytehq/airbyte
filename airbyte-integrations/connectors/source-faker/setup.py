#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["airbyte-cdk~=0.2", "mimesis==6.1.1"]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "source-acceptance-test",
]

setup(
    name="source_faker",
    description="Source implementation for fake but realistic looking data.",
    author="Airbyte",
    author_email="evan@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
