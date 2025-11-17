---
products: all
---

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { faCircleCheck } from "@fortawesome/free-solid-svg-icons";
import { faSlack } from "@fortawesome/free-brands-svg-icons";

# Connector support levels

This page describes the different types of connectors in Airbyte, how they're supported and maintained, and who can use them.

## Support by Airbyte plan

Your service level depends on your support plan and contract. If you need stricter SLAs, let the sales team know.

| Support level   | Core                                                | Cloud                                                                    | Self-Managed Enterprise                                                  | Notes                                  |
| --------------- | --------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | -------------------------------------- |
| **Airbyte**     | <FontAwesomeIcon icon={faSlack} /> Slack            | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported |                                        |
| **Enterprise**  | <FontAwesomeIcon icon={faCircleXmark} /> N/A        | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported |                                        |
| **Marketplace** | <FontAwesomeIcon icon={faCircleXmark} /> No support | <FontAwesomeIcon icon={faCircleXmark} /> No support                      | <FontAwesomeIcon icon={faCircleXmark} /> No support                      |                                        |
| **Custom**      | <FontAwesomeIcon icon={faSlack} /> Slack            | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported | <FontAwesomeIcon icon={faCircleCheck} className="good-icon" /> Supported | Airbyte makes its best effort to help. |

Read the rest of this article to understand each support level in more detail.

## Airbyte connectors

**Airbyte** connectors are maintained and supported by Airbyte to a high quality standard. These connectors:

- Are tested, vetted, and production ready for everyone.
- Are officially supported and maintained by Airbyte.
- Experience few breaking changes. In the event you need to upgrade, you receive an adequate upgrade window.

## Enterprise connectors

**Enterprise** Connectors are premium connectors available exclusively for enterprise customers. These connectors:

- Are tested, vetted, and production ready for enterprise customers only, at **an additional cost**.
- Are officially supported and maintained by Airbyte.
- Experience few breaking changes. In the event you need to upgrade, you receive an adequate upgrade window.
- Provide enhanced capabilities and support for critical enterprise systems.
- Support larger data sets and parallelism for faster data transfers

## Marketplace connectors

**Marketplace** connectors are maintained by Airbyte's community members. These connectors:

- Are maintained by [by people like you](/community/contributing-to-airbyte/) for everyone to use.
- Aren't officially supported by Airbyte.
- Should be used with caution in production.
- Might not be feature complete and might experience backward-incompatible, breaking changes with no notice.

Connector documentation shows the usage and success rate to help you decide on each connector's reliability.

## Custom connectors

**Custom** connectors are connectors you build and maintain yourself for your workspace exclusively. You alone are responsible for their quality and production readiness. Official Support SLAs are only available if you have Premium Support included in your contract.

## Archived connectors

From time to time, Airbyte removes a connector. This is typically due to low use and/or lack of maintenance from the Community. This is necessary to ensure that the Connector Catalog maintains a minimum level of quality.

Archived connectors don't receive any further updates or support from the Airbyte team. Archived connectors remain source-available in the [`airbytehq/connector-archive`](https://github.com/airbytehq/connector-archive) repository on GitHub.

To take over the maintenance of an archived connector, open a [Github Discussion](https://github.com/airbytehq/airbyte/discussions/). Connectors must pass [Acceptance Tests](/platform/connector-development/testing-connectors/connector-acceptance-tests-reference) before you can start the un-archiving process.
