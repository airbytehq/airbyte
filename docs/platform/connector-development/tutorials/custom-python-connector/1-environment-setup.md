# Environment setup

This section walks you through setting up your development environment and creating the initial connector project structure. By the end of this section, you'll have a working connector skeleton that you can run locally.

## Prerequisites

Before starting, ensure you have the following tools installed:

- **Python 3.10 or higher**: Required for connector development.
- **Poetry**: Used for Python dependency management. Install it from [python-poetry.org](https://python-poetry.org/docs/#installation).
- **Git**: For version control.

For a complete list of recommended development tools, see [Developing Connectors Locally](../../local-connector-development.md).

## Clone the repository

Start by cloning the Airbyte repository (optionally fork it first if you plan to contribute):

```bash
git clone git@github.com:airbytehq/airbyte.git
cd airbyte
```

## Create the connector directory structure

Create a new directory for your connector. For this tutorial, we'll create a connector called `source-survey-monkey-demo`:

```bash
mkdir -p airbyte-integrations/connectors/source-survey-monkey-demo
cd airbyte-integrations/connectors/source-survey-monkey-demo
```

## Initialize the Poetry project

Initialize a new Poetry project and add the Airbyte CDK as a dependency:

```bash
poetry init --name source-survey-monkey-demo --python "^3.10" -n
poetry add airbyte-cdk
```

Now update the `pyproject.toml` to add the script entry point and package configuration. Replace the contents with:

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "source-survey-monkey-demo"
version = "0.1.0"
description = "Source connector for Survey Monkey API (tutorial)"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"

[[tool.poetry.packages]]
include = "source_survey_monkey_demo"

[tool.poetry.dependencies]
python = "^3.10"
airbyte-cdk = "^6.0"

[tool.poetry.scripts]
source-survey-monkey-demo = "source_survey_monkey_demo.run:run"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
```

## Create the source module

Create the source module directory and the required files:

```bash
mkdir -p source_survey_monkey_demo/schemas
mkdir -p secrets
mkdir -p integration_tests
```

### Create the `__init__.py` file

Create `source_survey_monkey_demo/__init__.py`:

```python
#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from .source import SourceSurveyMonkeyDemo

__all__ = ["SourceSurveyMonkeyDemo"]
```

### Create the source implementation

Create `source_survey_monkey_demo/source.py` with a basic template:

```python
#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


class SourceSurveyMonkeyDemo(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return []
```

### Create the run entry point

Create `source_survey_monkey_demo/run.py`:

```python
#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import sys

from airbyte_cdk.entrypoint import launch

from source_survey_monkey_demo import SourceSurveyMonkeyDemo


def run():
    source = SourceSurveyMonkeyDemo()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
```

### Create the main entry point

Create `main.py` in the connector root directory:

```python
#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from source_survey_monkey_demo.run import run

if __name__ == "__main__":
    run()
```

### Create the connector specification

Create `source_survey_monkey_demo/spec.yaml`:

```yaml
documentationUrl: https://docs.airbyte.com/integrations/sources/survey-monkey
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Survey Monkey Demo Spec
  type: object
  required:
    - access_token
  properties:
    access_token:
      type: string
      description: Access token for Survey Monkey API
      order: 0
      airbyte_secret: true
```

### Create a placeholder schema

Create `source_survey_monkey_demo/schemas/surveys.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {}
}
```

## Create test configuration files

### Create the secrets configuration

Create `secrets/config.json` with your Survey Monkey API access token:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_HERE"
}
```

:::caution
The `secrets/` directory is excluded from Git by default. Never commit your API credentials to version control.
:::

### Create the configured catalog

Create `integration_tests/configured_catalog.json`:

```json
{
  "streams": [
    {
      "stream": {
        "name": "surveys",
        "json_schema": {},
        "supported_sync_modes": ["full_refresh"]
      },
      "sync_mode": "full_refresh",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```

## Install dependencies

Install the project dependencies:

```bash
poetry install
```

## Verify the setup

Run the spec command to verify your connector is properly configured:

```bash
poetry run source-survey-monkey-demo spec
```

You should see output similar to:

```json
{
  "type": "SPEC",
  "spec": {
    "documentationUrl": "https://docs.airbyte.com/integrations/sources/survey-monkey",
    "connectionSpecification": {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "Survey Monkey Demo Spec",
      "type": "object",
      "required": ["access_token"],
      "properties": {
        "access_token": {
          "type": "string",
          "description": "Access token for Survey Monkey API",
          "order": 0,
          "airbyte_secret": true
        }
      }
    }
  }
}
```

Run the check command to verify the connection (this will succeed because our placeholder implementation always returns true):

```bash
poetry run source-survey-monkey-demo check --config secrets/config.json
```

You should see:

```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "SUCCEEDED"
  }
}
```

## Project structure

Your connector directory should now have this structure:

```text
source-survey-monkey-demo/
  main.py
  pyproject.toml
  poetry.lock
  source_survey_monkey_demo/
    __init__.py
    run.py
    source.py
    spec.yaml
    schemas/
      surveys.json
  secrets/
    config.json
  integration_tests/
    configured_catalog.json
```

You're now ready to start development. In the [next section](./2-reading-a-page.md), we'll implement the surveys stream to read data from the Survey Monkey API.
