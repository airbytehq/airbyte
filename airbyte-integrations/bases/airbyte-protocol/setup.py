#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import setuptools

setuptools.setup(
    name="airbyte-protocol",
    description="Contains classes representing the schema of the Airbyte protocol.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    package_data={"": ["models/yaml/*.yaml"]},
    install_requires=["PyYAML==5.4", "pydantic==1.6.*"],
)
