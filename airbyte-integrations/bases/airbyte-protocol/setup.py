#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import setuptools

MAIN_REQUIREMENTS = (
    "PyYAML==5.4",
    "pydantic==1.6.*",
    # the new version (>= 2.1.0) of package markupsafe removed the funcion `soft_unicode`. And it broke other dependences
    # https://github.com/pallets/markupsafe/blob/main/CHANGES.rst
    # thus this version is pinned
    "markupsafe==2.0.1",
)

setuptools.setup(
    name="airbyte-protocol",
    description="Contains classes representing the schema of the Airbyte protocol.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    package_data={"": ["models/yaml/*.yaml"]},
    install_requires=MAIN_REQUIREMENTS,
)
