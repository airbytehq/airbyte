#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import setuptools

setuptools.setup(
    name="base-python",
    description="Contains machinery to make it easy to write an integration in python.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    package_data={"": ["models/yaml/*.yaml"]},
    install_requires=[
        "PyYAML==5.4",
        "pydantic==1.6.*",
        "airbyte-protocol",
        "jsonschema==3.2.0",
        "requests",
        "backoff",
        "pytest",
        "pendulum",
    ],
    entry_points={
        "console_scripts": ["base-python=base_python.entrypoint:main"],
    },
)
