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
        "airbyte-protocol",
        "backoff",
        "jsonschema==3.2.0",
        "pendulum",
        "pydantic==1.6.*",
        "pytest",
        "PyYAML==5.4",
        "requests",
    ],
    entry_points={
        "console_scripts": ["base-python=base_python.entrypoint:main"],
    },
)
