#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from setuptools import find_packages, setup

TEST_REQUIREMENTS = [
    "pytest~=6.1",
]

setup(
    name="ci_static_check_reports",
    description="CI tool to detect changed modules and then generate static check reports.",
    author="Airbyte",
    author_email="contact@airbyte.io",
    packages=find_packages(),
    install_requires=["invoke~=1.6.0", "virtualenv~=20.10.0"],
    package_data={"": ["*.json", "schemas/*.json"]},
    extras_require={
        "tests": TEST_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "ci_detect_changed_modules = ci_detect_changed_modules.main:main",
            "ci_build_python_checkers_reports = ci_build_python_static_checkers_reports.main:main",
        ],
    },
)
