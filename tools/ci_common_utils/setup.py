#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["cryptography", "requests", "pyjwt~=2.3.0"]

TEST_REQUIREMENTS = ["requests-mock"]

setup(
    version="0.0.0",
    name="ci_common_utils",
    description="Suite of all often used classes and common functions",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    python_requires=">=3.9",
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
)
