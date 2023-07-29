#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    # using a fork until https://github.com/4n4nd/prometheus-api-client-python/pull/267 get merged
    "prometheus-api-client @ git+https://github.com/samber/prometheus-api-client-python.git@03ee103#egg=prometheus-api-client",
]

TEST_REQUIREMENTS = [
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
]

setup(
    name="source_prometheus",
    description="Source implementation for Prometheus.",
    author="Samuel Berthe",
    author_email="samuel@screeb.app",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml", "schemas/*.json", "schemas/shared/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
