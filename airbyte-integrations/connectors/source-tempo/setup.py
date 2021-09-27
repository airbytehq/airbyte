#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_tempo",
    description="Source implementation for Tempo.",
    author="Thomas van Latum",
    author_email="thomas@gcompany.nl",
    packages=find_packages(),
    install_requires=["airbyte-protocol", "base-python", "requests", "pytest==6.1.2"],
    package_data={"": ["*.json", "schemas/*.json"]},
)
