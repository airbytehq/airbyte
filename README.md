# HashiCorp Vault Source

This is the repository for the HashiCorp Vault source connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/vault).

## Local development

### Prerequisites

- Python (~=3.10)
- Poetry (~=1.7) - installation instructions [here](https://python-poetry.org/docs/#installation)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

### Create credentials

You'll need a HashiCorp Vault instance with AppRole authentication enabled. Create a `secrets/config.json` file with the following structure:

```json
{
  "vault_url": "https://your-vault-instance.com",
  "role_id": "your-role-id",
  "secret_id": "your-secret-id",
  "namespace": "admin",
  "verify_ssl": true
}
```

Note that the `namespace` parameter is optional:
- For HCP Vault (HashiCorp Cloud Platform), use `"admin"`
- For self-hosted Vault, use `"root"` or leave empty (`""`)

### Locally running the connector

```bash
poetry run source-vault spec
poetry run source-vault check --config secrets/config.json
poetry run source-vault discover --config secrets/config.json
poetry run source-vault read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Running unit tests

To run unit tests locally, from the connector directory run:

```bash
poetry run pytest unit_tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=source-vault build
```

An image will be available on your host with the tag `airbyte/source-vault:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/source-vault:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-vault:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-vault:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-vault:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Streams

This connector supports the following streams:

1. **vault_info** - Information about the Vault instance (full refresh)
2. **users** - User entities from Vault's identity system (full refresh)
3. **roles** - Authentication roles from various auth methods (full refresh)
4. **policies** - Access control policies (full refresh)
5. **groups** - Group entities from Vault's identity system (full refresh)
6. **namespaces** - Namespaces (Enterprise feature, recursive) (full refresh)
7. **secrets** - Secret names without values (recursive) (full refresh)
8. **identity_providers** - OIDC identity providers (full refresh)
9. **audit** - Audit logs and audit device information (incremental)

### Audit Stream Details

The **audit** stream supports incremental sync and retrieves:
- Information about configured audit devices
- Audit log entries (when accessible)

**Note on Audit Logs**: HashiCorp Vault typically writes audit logs to files, syslog, or sockets, which are not directly accessible via the Vault API. The audit stream currently returns information about configured audit devices. To access actual audit log entries, you would need to:

1. Configure Vault to write audit logs to a location accessible by the connector
2. Extend the connector to read from that location (file system, database, etc.)
3. Parse and process the audit log entries

The audit stream uses the `timestamp` field as the cursor for incremental syncs, allowing you to sync only new audit records since the last sync.

## Features

- Supports AppRole authentication
- Handles both HCP Vault and self-hosted Vault instances
- Recursively discovers namespaces and secrets
- Retrieves metadata without exposing secret values
- Configurable SSL verification
- Incremental sync support for audit logs