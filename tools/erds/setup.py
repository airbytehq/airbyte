#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import setuptools

setuptools.setup(
    name="erd_generator",
    description="Generates ERDs",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=["airbyte-cdk==0.1.60"],
    package_data={"": ["*.yml"]},
    setup_requires=[],
    entry_points={
        "console_scripts": [],
    },
    extras_require={
        "tests": ["pytest"],
    },
)
