# Grafana
This directory contains the manifest-only connector for `source-grafana`.

Grafana is an observability and analytics platform that lets teams visualize, explore, and alert on their data from dozens of sources in one place. This connector replicates Grafana resources such as datasources, dashboards, folders, and users into your warehouse or lake, so you can audit configuration changes, analyze usage, and join Grafana metadata with the rest of your operational data. By syncing Grafana objects on a schedule, you can track how dashboards evolve over time, understand which teams and visualizations are most active, and build governance and reliability reporting on top of your Grafana estate.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-grafana:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-grafana build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-grafana test
```

