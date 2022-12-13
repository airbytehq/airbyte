#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["requests", "PyYAML~=6.0", "GitPython~=3.1.29"]


setup(
    version="0.1.0",
    name="ci_connector_ops",
    description="Packaged maintained by the connector operations team to perform CI for connectors",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "check-test-strictness-level = ci_connector_ops.check_test_strictness_level:main",
        ],
    },
)
