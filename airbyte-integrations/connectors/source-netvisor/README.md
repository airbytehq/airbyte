# Netvisor

This directory contains the manifest-only `source-netvisor` connector. It reads accounting and reference data from Netvisor test and production environments.

See the [Netvisor connector documentation](https://docs.airbyte.com/integrations/sources/netvisor) for credentials, API permissions, supported streams, sync behavior, and limitations.

## Development

The connector is defined in `manifest.yaml`, with shared request signing, XML normalization, and schemas. It does not require custom Python components. You can import the manifest into Connector Builder to test changes with your own Netvisor credentials.

Follow the [local connector development guide](https://docs.airbyte.com/platform/connector-development/local-connector-development) to install the repository tooling. From this directory, run:

```bash
poe install
poe test-all
```

The standard spec test runs without customer credentials. Live connection and read tests require a Netvisor test company and credentials configured through Airbyte's test tooling. Keep credentials out of the repository and test fixtures.

The SVG icon uses the unchanged logo mark from Netvisor's [official brand assets](https://netvisor.fi/press/) on a square canvas.
