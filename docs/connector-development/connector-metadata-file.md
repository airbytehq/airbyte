# Connector Metadata.yaml File

The `metadata.yaml` file is a new addition to Airbyte's connector folders. This file is created with the goal of simplifying and enhancing how we manage information related to each connector. It is designed to replace the previous `source_definitions.yaml` and `destinations_definitions.yaml` files.

The `metadata.yaml` file contains crucial information about the connector, including its type, definition ID, Docker image tag, Docker repository, and much more. It plays a key role in the way Airbyte handles connector data and improves the overall organization and accessibility of this data.

## Structure

Below is an example of a `metadata.yaml` file for the Postgres source:

```yaml
data:
  allowedHosts:
    hosts:
      - ${host}
      - ${tunnel_method.tunnel_host}
  connectorSubtype: database
  connectorType: source
  definitionId: decd338e-5647-4c0b-adf4-da0e75f5a750
  dockerImageTag: 2.0.28
  maxSecondsBetweenMessages: 7200
  dockerRepository: airbyte/source-postgres
  githubIssueLabel: source-postgres
  icon: postgresql.svg
  license: MIT
  name: Postgres
  registries:
    cloud:
      dockerRepository: airbyte/source-postgres-strict-encrypt
      enabled: true
    oss:
      enabled: true
  releaseStage: generally_available
  supportUrl: https://docs.airbyte.com/integrations/sources/postgres
metadataSpecVersion: "1.0"
```

## The 'registries' Section

The `registries` section within the `metadata.yaml` file plays a vital role in determining the contents of the `oss_registry.json` and `cloud_registry.json` files.

This section contains two subsections: `cloud` and `oss` (Open Source Software). Each subsection contains details about the specific registry, such as the Docker repository associated with it and whether it's enabled or not.

### Structure

Here's how the `registries` section is structured in our previous `metadata.yaml` example:

```yaml
  registries:
    cloud:
      dockerRepository: airbyte/source-postgres-strict-encrypt
      enabled: true
    oss:
      enabled: true
```

In this example, both `cloud` and `oss` registries are enabled, and the Docker repository for the `cloud` registry is overrode to `airbyte/source-postgres-strict-encrypt`.

### Updating Registries

When the `metadata.yaml` file is updated, this data is automatically uploaded to Airbyte's metadata service. This service then generates the publicly available `oss_registry.json` and `cloud_registry.json` registries based on the information provided in the `registries` section.

For instance, if a connector is listed as `enabled: true` under the `oss` section, it will be included in the `oss_registry.json` file. Similarly, if it's listed as `enabled: true` under the `cloud` section, it will be included in the `cloud_registry.json` file.

Thus, the `registries` section in the `metadata.yaml` file provides a flexible and organized way to manage which connectors are included in each registry.
