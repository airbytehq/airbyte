#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.36",
    "cached_property==1.5.2",
    "facebook_business==17.0.0",
    "pendulum>=2,<3",
]

TEST_REQUIREMENTS = ["requests-mock~=1.9.3", "pytest~=6.1", "pytest-mock~=3.6", "requests_mock~=1.8", "freezegun"]

setup(
    name="source_facebook_marketing",
    description="Source implementation for Facebook Marketing.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={
        "": [
            # Include yaml files in the package (if any)
            "*.yml",
            "*.yaml",
            # Include all json files in the package, up to 4 levels deep
            "*.json",
            "*/*.json",
            "*/*/*.json",
            "*/*/*/*.json",
            "*/*/*/*/*.json",
        ]
    },
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "source-facebook-marketing=source_facebook_marketing.run:run",
        ],
    },
)
