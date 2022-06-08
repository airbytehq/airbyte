# ERD Generator

This module contains the code used to generate ERD diagrams for connectors. It is split into two main scripts:

- `generate.sh`: generates a DBML file for a given connector
- `publish.sh`: publishes an ERD for a connector to dbdocs.io
- the Python module (requires 3.9) `erd_generator` is used to parse AirbyteProtocol JSONSchema conveniently

## How this is integrated into the build lifecycle

See the Github action `.github/actions/publish-connector-erds/action.yml` and the `.github/workflows/publish-command.yml` scripts to see how this is
used. TL;DR ERDs are published when the `/publish` command runs successfully for a connector

## Assumptions made by this module

1. Only allowed connectors can publish ERDs. See `allowlist.txt` for the list of allowed connectors.
2. To publish an ERD for a connector, it must have a `secrets/config.json` which can be used to obtain its catalog. Any other config name currently
   does not work.
