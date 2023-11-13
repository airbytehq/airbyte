import ConnectorRegistry from '@site/src/components/ConnectorRegistry';

# Connector Catalog

## Connector Support Levels

Airbyte uses a two tiered system for connectors to help you understand what to expect from a connector:

**Certified**: A certified connector is actively maintained and supported by the Airbyte team and maintains a high quality bar. It is production ready.

**Community**: A community connector is maintained by the Airbyte community until it becomes Certified. Airbyte has over 800 code contributors and 15,000 people in the Slack community to help. The Airbyte team is continually certifying Community connectors as usage grows. As these connectors are not maintained by Airbyte, we do not offer support SLAs around them, and we encourage caution when using them in production.

For more information about the system, see [Product Support Levels](https://docs.airbyte.com/project-overview/product-support-levels)

_[View the connector registries in full](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html)_

## Sources

<ConnectorRegistry type="source"/>

## Destinations

<ConnectorRegistry type="destination"/>
