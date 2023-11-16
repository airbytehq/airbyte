#!/bin/bash

# Install airbyte-ci development version
pipx install --editable --force --python=python3.10 airbyte-ci/connectors/pipelines/
echo "Development version of airbyte-ci installed."
