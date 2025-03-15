---
products: all
---

# Connector Support Levels

The following table describes the support levels of Airbyte connectors.

|                                      | Airbyte Connector     | Marketplace                                                                                                                      | Custom             |
| ------------------------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| **Who maintains them?**              | The Airbyte team      | Users and the community, using [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) | Users              |
| **Production Readiness**             | Guaranteed by Airbyte | Airbyte does not guarantee any SLAs on Marketplace Connectors, but we provide data about their popularity and success rates      | Not guaranteed     |
| **Support: Cloud**                   | Supported\*           | No Support                                                                                                                       | Supported\*\*      |
| **Support: Powered by Airbyte**      | Supported\*           | No Support                                                                                                                       | Supported\*\*      |
| **Support: Self-Managed Enterprise** | Supported\*           | No Support                                                                                                                       | Supported\*\*      |
| **Support: Community (OSS)**         | Slack Support only    | No Support                                                                                                                       | Slack Support only |

\*For Airbyte Connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. Otherwise, please use our support portal and we will address
your issues as soon as possible.

\*\*For Custom connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. This support is provided with best efforts, and
maintenance/upgrades are owned by the customer.

## Airbyte Connectors

An **Airbyte Connector** is actively maintained and supported by the Airbyte team and maintains a
high quality bar. It is production ready.

### What you should know about Airbyte Connectors:

- Airbyte Connectors are officially supported by Airbyte and are available to all users.
- These connectors have been tested and vetted. They are production ready.
- Airbyte Connectors should go through minimal breaking change but in the event an upgrade is
  needed users will be given an adequate upgrade window.

## Marketplace

A **Marketplace** connector is maintained by the community members until it becomes an official Airbyte Connector. Airbyte
has over 800 code contributors and 15,000 people in the Slack community to help. The Airbyte team is
continually reviewing Marketplace connectors as usage grows to determine when a Marketplace connector should become an Airbyte Connector. Marketplace connectors are not maintained
by Airbyte and we do not offer support SLAs around them. We encourage caution when using them in
production.

### What you should know about Marketplace connectors:

- Marketplace connectors are available to all users.
- Marketplace connectors may be upgraded to an official Airbyte Connector at any time, and we will notify users of these
  upgrades via our Slack Community and in our Connector Catalog.
- Marketplace connectors might not be feature-complete (features planned for release are under
  development or not prioritized) and may include backward-incompatible/breaking API changes with no
  or short notice.
- Marketplace connectors have no Support SLAs.
- You're very welcome to contribute new features and streams to an existing Marketplace connector. Airbyte Contributor Experience team is happy to review PRs when we have capacity.

## Archived

From time to time, Airbyte will remove a connector from the Connector Catalog. This is typically due
extremely low usage and/or if the connector is no longer maintained by the community. This is
necessary to ensure that the Connector Catalog maintains a minimum level of quality.

Archived connectors will not receive any further updates or support from the Airbyte team. Archived
connectors remain source-available in the
[`airbytehq/connector-archive`](https://github.com/airbytehq/connector-archive) repository on
GitHub.

If you wish to take over the maintenance of an archived connector, please open a Github Discussion.
For API Sources (python), updating the connector to the latest version of the
[CDK](/connector-development/cdk-python/) and ensuring that the connector successfully passes the
[Connector Acceptance Tests](/connector-development/testing-connectors/connector-acceptance-tests-reference)
is the start to the un-archiving process.
