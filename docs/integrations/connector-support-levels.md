---
products: all
---

# Connector support levels

The following table describes the support levels of Airbyte connectors.

|                                      | Airbyte     | Enterprise             | Marketplace                                                                                                                | Custom         |
| ------------------------------------ | ----------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------- |
| **Who maintains them?**              | Airbyte     | Airbyte                | The community, using the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) | You            |
| **Production readiness**             | Guaranteed  | Guaranteed             | No SLAs, docs show their popularity and success rate data                                                                  | Not guaranteed |
| **Support: Cloud**                   | Supported\* | Supported\*            | No Support                                                                                                                 | Supported\*\*  |
| **Support: Powered by Airbyte**      | Supported\* | Supported\*            | No Support                                                                                                                 | Supported\*\*  |
| **Support: Self-Managed Enterprise** | Supported\* | Supported\*            | No Support                                                                                                                 | Supported\*\*  |
| **Support: Self-Managed Community**  | Slack only  | N/A                    | No Support                                                                                                                 | Slack only     |
| **Who can use them**                 | Everyone    | Extra license required | Everyone                                                                                                                   | You            |

\*For Airbyte Connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. Otherwise, please use our support portal and we will address
your issues as soon as possible.

\*\*For Custom connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. This support is provided with best efforts, and
maintenance/upgrades are owned by the customer.

## Airbyte connectors

**Airbyte** connectors are maintained and supported by Airbyte to a high quality standard. These connectors:

- Are tested, vetted, and production ready.
- Are officially supported by Airbyte and are available to all users.
- Experience few breaking changes. In the event an upgrade is needed, you receive an adequate upgrade window.

## Enterprise connectors

**Enterprise** Connectors are premium connectors available exclusively for Self-Managed Enterprise and Cloud Teams customers at **an additional cost**. These connectors:

- Are built and maintained by the Airbyte team.
- Provide enhanced capabilities and support for critical enterprise systems.
- Are not available to Open Source or standard Cloud customers.
- Support for larger data sets, parallelism for faster data transfers, and are covered under Airbyte's support SLAs.

## Marketplace connectors

**Marketplace** connectors are maintained by Airbyte's community members. These connectors:

- Are not maintained by Airbyte.
- Do not have support SLAs.
- Should be used with caution in production.
- Might not be feature complete and may experience backward-incompatible, breaking changes with no notice.
- Are available to everyone.
- Can [be improved by people like you](../platform/contributing-to-airbyte/).

## Custom connectors

**Custom** connectors are connectors you build and maintain yourself for your workspace exclusively. You alone are responsible for their quality and production readiness. Official Support SLAs are only available if you have Premium Support included in your contract.

## Archived connectors

From time to time, Airbyte removes a connector. This is typically due to low use and/or lack of maintenance from the Community. This is necessary to ensure that the Connector Catalog maintains a minimum level of quality.

Archived connectors don't receive any further updates or support from the Airbyte team. Archived connectors remain source-available in the [`airbytehq/connector-archive`](https://github.com/airbytehq/connector-archive) repository on GitHub.

To take over the maintenance of an archived connector, open a [Github Discussion](https://github.com/airbytehq/airbyte/discussions/). Connectors must pass [Acceptance Tests](/platform/connector-development/testing-connectors/connector-acceptance-tests-reference) before you can start the un-archiving process.
