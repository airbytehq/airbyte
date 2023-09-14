# connector_ops

A collection of utilities for working with Airbyte connectors.

# Setup

## Prerequisites

#### Poetry

Before you can start working on this project, you will need to have Poetry installed on your system. Please follow the instructions below to install Poetry:

1. Open your terminal or command prompt.
2. Install Poetry using the recommended installation method:

```bash
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.5.1 python3 -
```

Alternatively, you can use `pip` to install Poetry:

```bash
pip install --user poetry
```

3. After the installation is complete, close and reopen your terminal to ensure the newly installed `poetry` command is available in your system's PATH.

For more detailed instructions and alternative installation methods, please refer to the official Poetry documentation: https://python-poetry.org/docs/#installation

### Using Poetry in the Project

Once Poetry is installed, you can use it to manage the project's dependencies and virtual environment. To get started, navigate to the project's root directory in your terminal and follow these steps:


## Installation
```bash
poetry install
```


## Testing Locally

Simply run
```bash
poetry run pytest
```