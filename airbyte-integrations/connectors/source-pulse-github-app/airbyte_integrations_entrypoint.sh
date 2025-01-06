#!/usr/bin/env bash
set -e

# Entry point for the Airbyte connector container.
# It runs the connector with the provided arguments.
exec python -m source_pulse_github_app "$@"