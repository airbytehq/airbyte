from setuptools import find_packages, setup

setup(
    name="source_airmeet",
    version="0.1.0",
    description="Source implementation for Airmeet",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "airbyte-cdk>=0.80.0",
        "requests>=2.31.0",
    ],
    package_data={"": ["*.json", "*.yaml"],
                  "source_airmeet": ["schemas/*.json"]},
    entry_points={
        "console_scripts": [
            "source-airmeet=source_airmeet.main:main",
        ],
    },
)