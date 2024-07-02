# Migrate connector to use Poetry and base Docker Image

1. Remove the `Dockerfile` and `.dockerignore`
2. Include the `baseImage` to the `metadata.yaml` file. For now, look for `baseImage` to find examples:
```yaml
data:
  allowedHosts:
    hosts:
      - *
  connectorBuildOptions:
    baseImage: docker.io/airbyte/python-connector-base:1.2.0@sha256:c22a9d97464b69d6ef01898edf3f8612dc11614f05a84984451dde195f337db9
  connectorSubtype: api
  connectorType: source
  dockerImageTag: 0.1.0
```
3. Create a file called `pyproject.toml` and transfer all lib used in `setup.py` to this file

* `setup.py`
```python
from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk~=0.1",
]

TEST_REQUIREMENTS = [
    "requests-mock~=1.9.3",
    "pytest~=6.2",
    "pytest-mock~=3.6.1",
    "connector-acceptance-test",
]

setup(
    entry_points={
        "console_scripts": [
            "source-openweather=source_openweather.run:run",
        ],
    },
    name="source_openweather",
    description="Source implementation for Openweather.",
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
)
```

* `pyproject.toml` 
```toml
[build-system]
requires = [ "poetry-core>=1.0.0",]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
version = "0.2.1"
name = "source-openweather"
description = "Source implementation for Open Weather."
authors = [ "Airbyte <contact@airbyte.io>",]
license = "MIT"
readme = "README.md"
documentation = "https://docs.airbyte.com/integrations/sources/orb"
homepage = "https://airbyte.com"
repository = "https://github.com/airbytehq/airbyte"
[[tool.poetry.packages]]
include = "source_openweather"

[tool.poetry.dependencies]
python = "^3.9,<3.12"
airbyte-cdk = "^0.74.0"

[tool.poetry.scripts]
source-openweather = "source_openweather.run:run"

[tool.poetry.group.dev.dependencies]
pytest = "^6.2"
requests-mock = "^1.11.0"
pytest-mock = "^3.6.1"
```
4. Delete the `setup.py` file
5. Go to the connector folder and run `poetry lock` to generate the poetry file
6. Make sure the `run.py` exist, if not create one:
```
import sys

from airbyte_cdk.entrypoint import launch
from source_openweather import SourceOpenweather


def run():
    source = SourceOpenweather()
    launch(source, sys.argv[1:])
```
