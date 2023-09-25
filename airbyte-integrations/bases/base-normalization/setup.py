#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# Note: cattrs is pinned to the last known working version which does not have conflicts with typing_extensions.  Learn more https://airbytehq-team.slack.com/archives/C03C4AVJWG4/p1685546430990049

import setuptools

setuptools.setup(
    name="normalization",
    description="Normalizes data in the destination.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    url="https://github.com/airbytehq/airbyte",
    packages=setuptools.find_packages(),
    install_requires=["airbyte-cdk", "pyyaml", "jinja2", "types-PyYAML", "cattrs==22.2.0"],
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
