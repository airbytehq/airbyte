#!/bin/bash

# Fetches the latest binary release of Flow and writes the binaries to the `flow-bin/` directory.
# The release name is read from the `FLOW_RELEASE` env variable, but it defaults to "dev".

FLOW_RELEASE="${FLOW_RELEASE:-dev}"
mkdir -p flow-bin
rm -f flow-bin/*
cd flow-bin && curl -L --proto '=https' --tlsv1.2 -sSf "https://github.com/estuary/flow/releases/download/${FLOW_RELEASE}/flow-x86-linux.tar.gz" | tar -zx 
