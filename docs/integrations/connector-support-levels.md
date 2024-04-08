---
products: all
---

# Connector Support Levels

The following table describes the support levels of Airbyte connectors.

|                                      | Certified                                 | Community                                                                                              | Custom                                                                                                                                                                                                                                                             |
| ------------------------------------ | ----------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Availability**                     | Available to all users                    | Available to all users                                                                                 | Available to all users                                                                                                                                                                                                                                             |
| **Who builds them?**                 | Either the community or the Airbyte team. | Typically they are built by the community. The Airbyte team may upgrade them to Certified at any time. | Anyone can build custom connectors. We recommend using our [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) or [Low-code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview). |
| **Who maintains them?**              | The Airbyte team                          | Users                                                                                                  | Users                                                                                                                                                                                                                                                              |
| **Production Readiness**             | Guaranteed by Airbyte                     | Not guaranteed                                                                                         | Not guaranteed                                                                                                                                                                                                                                                     |
| **Support: Cloud**                   | Supported\*                               | No Support                                                                                             | Supported\*\*                                                                                                                                                                                                                                                      |
| **Support: Powered by Airbyte**      | Supported\*                               | No Support                                                                                             | Supported\*\*                                                                                                                                                                                                                                                      |
| **Support: Self-Managed Enterprise** | Supported\*                               | No Support                                                                                             | Supported\*\*                                                                                                                                                                                                                                                      |
| **Support: Community (OSS)**         | Slack Support only                        | No Support                                                                                             | Slack Support only                                                                                                                                                                                                                                                 |

\*For Certified connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. Otherwise, please use our support portal and we will address
your issues as soon as possible.

\*\*For Custom connectors, Official Support SLAs are only available to customers with Premium
Support included in their contract. This support is provided with best efforts, and
maintenance/upgrades are owned by the customer.

## Certified

A **Certified** connector is actively maintained and supported by the Airbyte team and maintains a
high quality bar. It is production ready.

### What you should know about Certified connectors:

- Certified connectors are available to all users.
- These connectors have been tested and vetted in order to be certified and are production ready.
- Certified connectors should go through minimal breaking change but in the event an upgrade is
  needed users will be given an adequate upgrade window.

## Community

A **Community** connector is maintained by the Airbyte community until it becomes Certified. Airbyte
has over 800 code contributors and 15,000 people in the Slack community to help. The Airbyte team is
continually certifying Community connectors as usage grows. As these connectors are not maintained
by Airbyte, we do not offer support SLAs around them, and we encourage caution when using them in
production.

### What you should know about Community connectors:

- Community connectors are available to all users.
- Community connectors may be upgraded to Certified at any time, and we will notify users of these
  upgrades via our Slack Community and in our Connector Catalog.
- Community connectors might not be feature-complete (features planned for release are under
  development or not prioritized) and may include backward-incompatible/breaking API changes with no
  or short notice.
- Community connectors have no Support SLAs.

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
