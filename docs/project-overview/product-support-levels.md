# Connector Support Levels

The following table describes the support levels of Airbyte connectors.

|                                   | Certified                  | Custom                      | Community              |
| --------------------------------- | -------------------------- | -------------------------- | ---------------------- |
| **Availability**                      | Available to all users     | Available to all users     | Available to all users |
| **Support: Cloud**                    | Supported*                 | Supported**                | No Support |
| **Support: Powered by Airbyte**       | Supported*                 | Supported**                | No Support |
| **Support: Self-Managed Enterprise**  | Supported*                 | Supported**                | No Support |
| **Support: Community (OSS)**          | Slack Support only         | Slack Support only         | No Support |
| **Who builds them?**                  | Either the community or the Airbyte team. | Anyone can build custom connectors. We recommend using our [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) or [Low-code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview). | Typically they are built by the community. The Airbyte team may upgrade them to Certified at any time. |
| **Who maintains them?** | The Airbyte team | Users | Users |
| **Production Readiness** | Guaranteed by Airbyte | Not guaranteed | Not guaranteed |

\*For Certified connectors, Official Support SLAs are only available to customers with Premium Support included in their contract. Otherwise, please use our support portal and we will address your issues as soon as possible.

\*\*For Custom connectors, Official Support SLAs are only available to customers with Premium Support included in their contract. This support is provided with best efforts, and maintenance/upgrades are owned by the customer.

## Certified

A **Certified** connector is actively maintained and supported by the Airbyte team and maintains a high quality bar. It is production ready.

### What you should know about Certified connectors:

- Certified connectors are available to all users.
- These connectors have been tested and vetted in order to be certified and are production ready.
- Certified connectors should go through minimal breaking change but in the event an upgrade is needed users will be given an adequate upgrade window.

## Community

A **Community** connector is maintained by the Airbyte community until it becomes Certified. Airbyte has over 800 code contributors and 15,000 people in the Slack community to help. The Airbyte team is continually certifying Community connectors as usage grows. As these connectors are not maintained by Airbyte, we do not offer support SLAs around them, and we encourage caution when using them in production.

### What you should know about Community connectors:

- Community connectors are available to all users.
- Community connectors may be upgraded to Certified at any time, and we will notify users of these upgrades via our Slack Community and in our Connector Catalog.
- Community connectors might not be feature-complete (features planned for release are under development or not prioritized) and may include backward-incompatible/breaking API changes with no or short notice.
- Community connectors have no Support SLAs.
