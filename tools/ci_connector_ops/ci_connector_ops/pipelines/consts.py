#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
]

DEFAULT_PYTHON_EXCLUDE = ["**/.venv", "**/__pycache__"]
CI_CREDENTIALS_SOURCE_PATH = "tools/ci_credentials"
CI_CONNECTOR_OPS_SOURCE_PATH = "tools/ci_connector_ops"
