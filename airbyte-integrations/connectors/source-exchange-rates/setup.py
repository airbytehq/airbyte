#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

setup(
    name="source_exchange_rates",
    description="Source implementation for Exchange Rate API.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    package_data={"": ["*.json", "*.yaml", "schemas/*.json"]},
    install_requires=["airbyte-cdk~=0.1", "pendulum>=2,<3"],
)
