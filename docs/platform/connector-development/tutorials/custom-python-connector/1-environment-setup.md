# Environment setup

This guide will help you set up your development environment to build a custom Python connector using the Airbyte CDK.

## Prerequisites

Before starting, ensure you have the following installed and configured:

- **Python 3.10 or higher** ([download here](https://python.org/downloads/))
- **uv** for installing Python CLI applications ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Poe the Poet** for task management ([installation guide](https://poethepoet.natn.io/installation.html))
- **Docker** installed and running ([get Docker](https://docs.docker.com/get-docker/))
- **Gradle** for Java/Kotlin connector development ([installation guide](https://gradle.org/install/))
- **Git** configured with your credentials
- Basic familiarity with Python development

### Verify Your Setup

Run these commands to verify your environment is ready:

```bash
python --version  # Should show 3.10 or higher
uv --version      # Should show uv is installed
poe --version     # Should show Poe the Poet is installed
docker --version  # Should show Docker is installed
gradle --version  # Should show Gradle is installed
git --version     # Should show Git is installed
```

If any of these commands fail, please install the missing prerequisites before continuing.

## Choose Your Development Approach

**🎯 Recommended for most users:** Start with the [Connector Builder](../../connector-builder-ui/tutorial.mdx) - a visual tool that handles 90% of connector use cases without writing code.

**⚡ Advanced Python development:** Continue with this tutorial if you need:
- Complex authentication flows
- Custom data transformations  
- Advanced error handling
- Integration with existing Python libraries

## Create Your Connector Project

We'll create a standalone connector project for the Survey Monkey API. This approach is recommended over developing inside the main Airbyte repository.

```bash
# Install the Airbyte CDK CLI
uv tool install --upgrade 'airbyte-cdk[dev]'

# Create a new directory for your connector
mkdir source-survey-monkey-tutorial
cd source-survey-monkey-tutorial

# Initialize a new connector project using the CDK CLI
airbyte-cdk generate source --name source-survey-monkey --description "Survey Monkey API connector for Airbyte"

# This creates the basic project structure:
# - source_survey_monkey/
# - source_survey_monkey/__init__.py
# - source_survey_monkey/source.py
# - source_survey_monkey/spec.json
# - source_survey_monkey/run.py
# - pyproject.toml
```

## Create a Minimal Working Connector

Let's create a basic connector to verify everything is working correctly.

### 1. Create the main source file

Create `source_survey_monkey/source.py` with this content:

```python
from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import AirbyteConnectionStatus, Status

class SourceSurveyMonkey(AbstractSource):
    def check_connection(self, logger, config) -> tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        try:
            # For now, we'll just return success
            # In the next steps, we'll implement actual API connection testing
            return True, None
        except Exception as e:
            return False, f"Unable to connect: {e}"
    
    def streams(self, config) -> list[Stream]:
        """
        Returns a list of the streams that this source supports
        """
        # We'll implement actual streams in the following tutorial steps
        return []
```

### 2. Create the connector specification

Create `source_survey_monkey/spec.json` with this content:

```json
{
  "documentationUrl": "https://docs.airbyte.com/integrations/sources/survey-monkey",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Survey Monkey Source Spec",
    "type": "object",
    "required": ["access_token"],
    "properties": {
      "access_token": {
        "type": "string",
        "description": "Access Token for Survey Monkey API",
        "airbyte_secret": true
      }
    }
  }
}
```

### 3. Create the entry point script

Create `source_survey_monkey/run.py` with this content:

```python
import sys
from airbyte_cdk.entrypoint import launch
from .source import SourceSurveyMonkey

if __name__ == "__main__":
    source = SourceSurveyMonkey()
    launch(source, sys.argv[1:])
```

### 4. Install dependencies

The CDK CLI automatically creates a proper `pyproject.toml` file with all necessary dependencies and scripts. Install the project dependencies:

```bash
# Install connector dependencies using Poe
poe install
```

## Verify Your Setup

Test that your connector is working correctly:

```bash
# Test the spec command using airbyte-cdk CLI
airbyte-cdk test spec

# Alternative: Test using Poe tasks (recommended)
poe test-spec
```

You should see JSON output showing your connector's specification. If you see this output, congratulations! Your development environment is properly set up.

## Test Basic Operations

Let's test the other connector operations to make sure everything is working:

### Create a test configuration

Create a `secrets` directory and add a test config file:

```bash
mkdir secrets
echo '{"access_token": "test_token"}' > secrets/config.json
```

Note: The `secrets` directory is automatically ignored by git, so your credentials won't be accidentally committed.

### Test the check operation

```bash
# Using airbyte-cdk CLI
airbyte-cdk test check --config secrets/config.json

# Using Poe tasks (recommended)
poe test-check --config secrets/config.json
```

You should see output indicating a successful connection:

```json
{
  "type": "CONNECTION_STATUS",
  "connectionStatus": {
    "status": "SUCCEEDED"
  }
}
```

### Test the discover operation

```bash
# Using airbyte-cdk CLI
airbyte-cdk test discover --config secrets/config.json

# Using Poe tasks (recommended)
poe test-discover --config secrets/config.json
```

You should see output with an empty catalog (since we haven't implemented streams yet):

```json
{
  "type": "CATALOG",
  "catalog": {
    "streams": []
  }
}
```

### Additional Development Tasks

The official Airbyte development workflow uses Poe tasks for common operations:

```bash
# Run fast tests
poe test-fast

# Run unit tests
poe test-unit-tests

# Run integration tests
poe test-integration-tests

# Lint your code
poe lint

# Format your code
poe format
```

For a complete list of available tasks, run `poe --help` from your connector directory.

## What's Next?

Perfect! Your development environment is now set up and ready. You have:

✅ A working Python connector project  
✅ All prerequisites installed and verified  
✅ Basic connector operations tested  
✅ A foundation to build upon  

In the [next section](./2-reading-a-page.md), we'll implement the surveys stream to read data from the Survey Monkey API.

## Troubleshooting

### Common Issues

**`ModuleNotFoundError` when running commands:**
- Run `poe install` to install all dependencies
- Make sure you're in the correct project directory

**`Permission denied` errors with Docker:**
- Ensure Docker is running: `docker ps`
- On Linux, you may need to add your user to the docker group

**`Python version` errors:**
- Verify you're using Python 3.10+: `python --version`
- Consider using `pyenv` to manage multiple Python versions

**`uv not found`:**
- Install uv following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- Restart your terminal after installation

**`poe not found`:**
- Install Poe the Poet: `brew install poethepoet` or follow [installation guide](https://poethepoet.natn.io/installation.html)
- Restart your terminal after installation

**`airbyte-cdk command not found`:**
- Install the CDK CLI: `uv tool install --upgrade 'airbyte-cdk[dev]'`
- Ensure uv's tool bin directory is in your PATH

**Import errors in your connector:**
- Check that all files have the correct names and locations
- Ensure `__init__.py` files exist in your package directories

### Getting Help

- **Official Local Development Guide:** [Developing Connectors Locally](../../local-connector-development.md) - The authoritative guide for all connector development tooling
- **CDK Documentation:** [Airbyte Python CDK docs](https://airbytehq.github.io/airbyte-python-cdk/)
- **Contributing Guide:** [CDK Contributing Guide](https://github.com/airbytehq/airbyte-python-cdk/blob/main/docs/CONTRIBUTING.md)
- **Community Support:** [Airbyte Community Slack](https://airbyte.com/community)

If you're still having issues, the [Connector Builder](../../connector-builder-ui/tutorial.mdx) might be a better starting point for your use case.
