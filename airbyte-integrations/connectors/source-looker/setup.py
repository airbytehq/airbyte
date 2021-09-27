#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_looker",
    description="Source implementation for Looker.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-protocol", "base-python", "requests", "backoff", "pytest==6.1.2"],
    package_data={"": ["*.json", "schemas/*.json"]},
)
