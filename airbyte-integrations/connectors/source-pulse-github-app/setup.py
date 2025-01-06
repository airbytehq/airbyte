from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=0.42.0",
    "requests~=2.28",
    "pyjwt~=2.4",
    "python-dateutil~=2.8"
]

TEST_REQUIREMENTS = [
    "pytest>=7.0",
    "pytest-mock>=3.6"
]

setup(
    name="source_pulse_github_app",
    description="Airbyte Source for GitHub Identities and Audit Logs using a GitHub App named Pulse.",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    extras_require={
        "tests": TEST_REQUIREMENTS
    },
    package_data={"": ["*.json", "*.yaml"]},
    include_package_data=True,
    entry_points={
        "airbyte.source": "source_pulse_github_app = source_pulse_github_app.source:SourcePulseGithubApp"
    }
)
