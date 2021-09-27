#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_recurly",
    description="Source implementation for Recurly.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["airbyte-protocol", "base-python", "recurly==3.14.0", "requests", "pytest==6.1.2"],
    package_data={"": ["*.json", "schemas/*.json"]},
)
