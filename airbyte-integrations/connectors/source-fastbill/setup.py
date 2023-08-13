#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
]

<<<<<<< HEAD
TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
]
=======
TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest~=6.1", "pytest-mock~=3.6.1", "responses~=0.21.0"]
>>>>>>> 1219e66fb966f03620db5a2157148e8a5b28abdb

setup(
    name="source_fastbill",
    description="Source implementation for Fastbill.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
