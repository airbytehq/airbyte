#!/usr/bin/env bash
set -e

# Build SurveyCTO connector image
cd airbyte-integrations/connectors/source-surveycto && docker build . -t airbyte/source-surveycto:dev

# Build Commcare connector image
cd ../../../airbyte-integrations/connectors/source-commcare && docker build . -t airbyte/source-commcare:dev

cd ../../../ && docker compose up -d