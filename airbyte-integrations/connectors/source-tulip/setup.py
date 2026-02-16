from setuptools import setup, find_packages

setup(
    name="source-tulip",
    version="0.1.0",
    description="Airbyte source connector for Tulip Tables",
    packages=find_packages(),
    install_requires=["airbyte-cdk>=1.0", "requests"],
    python_requires=">=3.9",
    package_data={"source_tulip": ["spec.yaml", "schemas/*.json"]},
)
