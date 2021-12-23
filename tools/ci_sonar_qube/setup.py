#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

MAIN_REQUIREMENTS = ["requests", "ci_common_utils"]

TEST_REQUIREMENTS = ["requests-mock",  "pytest"]

setup(
    version="0.0.0",
    name="ci_sonar_qube",
    description="Load and extract CI secrets for test suites",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    python_requires='>=3.7',
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'ci_sonar_qube = ci_sonar_qube.main:main',
        ],
    },
)
