import ConnectorRegistry from '@site/src/components/ConnectorRegistry';

# Connector Catalog

## Connector Release Stages

Airbyte uses a grading system for connectors to help you understand what to expect from a connector:

**Generally Available**: A generally available connector has been deemed ready for use in a production environment and is officially supported by Airbyte. Its documentation is considered sufficient to support widespread adoption.

**Beta**: A beta connector is considered stable with no backwards incompatible changes but has not been validated by a broader group of users. We expect to find and fix a few issues and bugs in the release before it’s ready for GA.

**Alpha**: An alpha connector signifies a connector under development and helps Airbyte gather early feedback and issues reported by early adopters. We strongly discourage using alpha releases for production use cases and do not offer Cloud Support SLAs around these products, features, or connectors.

For more information about the grading system, see [Product Release Stages](https://docs.airbyte.com/project-overview/product-release-stages)

_[View the connector registries in full](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html)_

## Sources

<ConnectorRegistry type="source"/>

## Destinations

<ConnectorRegistry type="destination"/>
