#!/usr/bin/env bash

set -e

# TODO: replace with more general version
# hacky version that expects ordering of args "--config config.json --discover"
function check_connection() {
  if [[ "$1" == "--config" ]]; then
    echo "Config provided, running check connection."
    CONFIG_FILE=$2
    echo "Using config file \"$CONFIG_FILE\""
    STRIPE_KEY=$(jq -r ".client_secret" "$CONFIG_FILE")
    OUTPUT=$(curl https://api.stripe.com/v1/customers -u "$STRIPE_KEY:")

    if [[ "$OUTPUT" =~ .*"Invalid API Key".* ]]; then
      echo "Connection check failed."
      exit 2
    else
      echo "Connection checked and valid."
    fi
  else
    echo "No config, not running check_connection."
    exit 3
  fi
}

if [[ "$*" =~ .*"--discover".* ]]; then
  check_connection "$@"
  tap-stripe "$@"
else
  tap-stripe "$@"
fi
