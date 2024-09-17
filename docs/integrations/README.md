import ConnectorRegistry from '@site/src/components/ConnectorRegistry';

# Connector Catalog

## Introduction to Connectors

Each source or destination is a connector. A source is an API, file, database, or data warehouse that you want to ingest data from. A destination is a data warehouse, data lake, database, or an analytics tool where you want to load your ingested data. Connectors, therefore, can either pull data from a source, or push data to a destination. 

By browsing the catalog, you can see useful links to documentation, source code, and issues related to each connector. You'll also be able to see whether a connector is supported on our Open Source Software (OSS), our Cloud platform, or both. 

As an open source project, Airbyte's catalog of connectors is continually growing thanks to community contributions as well as development by the Airbyte team. Airbyte enables you to [build new connectors](/connector-development/). We encourage you to consider contributing  enhancements, bug fixes, or features to existing connectors or to submit entirely new connectors you've built for inclusion in the connector catalog. That said, you always have the option to publish connectors privately, to your own workspaces. 

Learn more about contributing to Airbyte [here](/contributing-to-airbyte/).

## Connector Support Levels

Airbyte uses a tiered system for connectors to help you understand what to expect from a connector. In short, there are three tiers: Airbyte Connectors, Marketplace Connectors, and Custom Connectors. Review the documentation on [connector support levels](./connector-support-levels.md) for details on each tier.

_[View the connector registries in full](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html)_

## Sources

<ConnectorRegistry type="source"/>

## Destinations

<ConnectorRegistry type="destination"/>
