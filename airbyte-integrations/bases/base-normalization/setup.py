#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import setuptools

setuptools.setup(
    name="normalization",
    description="Normalizes data in the destination.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=["airbyte-cdk", "pyyaml", "jinja2", "types-PyYAML"],
    package_data={"": ["*.yml"]},
    setup_requires=["pytest-runner"],
    entry_points={
        "console_scripts": [
            "transform-config=normalization.transform_config.transform:main",
            "transform-catalog=normalization.transform_catalog.transform:main",
        ],
    },
    extras_require={
        "tests": ["airbyte-cdk", "pytest", "mypy", "types-PyYAML"],
    },
)
