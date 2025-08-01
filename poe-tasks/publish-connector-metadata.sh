#!/usr/bin/env bash
set -euo pipefail

# This script wraps the `metadata_service validate` command.
# That Python script performs some basic checks that a connector has valid
# metadata.yaml and <name>.md docs file.

# read connectors list from stdin,
# somehow invoke `poetry run metadata_service validate airbyte-integrations/connectors/destination-bigquery/metadata.yaml docs/integrations/destinations/bigquery.md`
# (presumably need to install metadata_service?)
