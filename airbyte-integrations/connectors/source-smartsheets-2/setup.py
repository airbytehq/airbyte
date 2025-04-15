#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup


MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.2",
    "smartsheet-python-sdk~=3.0",
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest-mock~=3.6.1",
    "pytest~=6.2",
    # This is not a PyPI package, came with the template
    # Not sure how to integrate this but it breaks installing test dependencies
    # "connector-acceptance-test",
]

setup(
    name="source_smartsheets_2",
    description="An alternative source implementation for Smartsheets.",
    author="Canonical",
    author_email="jaas-crew@lists.canonical.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "source-smartsheets-2=source_smartsheets_2.run:run",
        ],
    },
)
