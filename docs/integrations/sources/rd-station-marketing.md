# RD Station Marketing

RD Station Marketing is the leading Marketing Automation tool in Latin America. It is a software application that helps your company carry out better campaigns, nurture Leads, generate qualified business opportunities and achieve more results. From social media to email, Landing Pages, Pop-ups, even Automations and Analytics.

## Prerequisites

- An RD Station account
- A callback URL to receive the first account credential (can be done using localhost)
- `client_id` and `client_secret` credentials. Access [this link](https://appstore.rdstation.com/en/publisher) to register a new application and start the authentication flow.

## Airbyte Open Source

- Start Date
- Client Id
- Client Secret
- Refresh token

## Supported sync modes

The RD Station Marketing source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental (for analytics endpoints)

## Supported Streams

- conversions (analytics endpoint)
- emails (analytics endpoint)
- funnel (analytics endpoint)
- workflow_emails_statistics (analytics endpoint)
- emails
- embeddables
- fields
- landing_pages
- popups
- segmentations
- workflows

## Performance considerations

Each endpoint has its own performance limitations, which also consider the account plan. For more informations, visit the page [API request limit](https://developers.rdstation.com/reference/limite-de-requisicoes-da-api?lng=en).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                          |
| :------ | :--------- | :-------------------------------------------------------- | :------------------------------- |
| 0.3.12 | 2025-02-01 | [53015](https://github.com/airbytehq/airbyte/pull/53015) | Update dependencies |
| 0.3.11 | 2025-01-25 | [52525](https://github.com/airbytehq/airbyte/pull/52525) | Update dependencies |
| 0.3.10 | 2025-01-18 | [51869](https://github.com/airbytehq/airbyte/pull/51869) | Update dependencies |
| 0.3.9 | 2025-01-11 | [51324](https://github.com/airbytehq/airbyte/pull/51324) | Update dependencies |
| 0.3.8 | 2024-12-28 | [50676](https://github.com/airbytehq/airbyte/pull/50676) | Update dependencies |
| 0.3.7 | 2024-12-21 | [50264](https://github.com/airbytehq/airbyte/pull/50264) | Update dependencies |
| 0.3.6 | 2024-12-14 | [49679](https://github.com/airbytehq/airbyte/pull/49679) | Update dependencies |
| 0.3.5 | 2024-12-12 | [49334](https://github.com/airbytehq/airbyte/pull/49334) | Update dependencies |
| 0.3.4 | 2024-12-11 | [48161](https://github.com/airbytehq/airbyte/pull/48161) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.3 | 2024-10-29 | [47936](https://github.com/airbytehq/airbyte/pull/47936) | Update dependencies |
| 0.3.2 | 2024-10-28 | [47577](https://github.com/airbytehq/airbyte/pull/47577) | Update dependencies |
| 0.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.3.0 | 2024-08-14 | [44081](https://github.com/airbytehq/airbyte/pull/44081) | Refactor connector to manifest-only format |
| 0.2.8 | 2024-08-10 | [43486](https://github.com/airbytehq/airbyte/pull/43486) | Update dependencies |
| 0.2.7 | 2024-08-03 | [43085](https://github.com/airbytehq/airbyte/pull/43085) | Update dependencies |
| 0.2.6 | 2024-07-27 | [42665](https://github.com/airbytehq/airbyte/pull/42665) | Update dependencies |
| 0.2.5 | 2024-07-20 | [42187](https://github.com/airbytehq/airbyte/pull/42187) | Update dependencies |
| 0.2.4 | 2024-07-13 | [41898](https://github.com/airbytehq/airbyte/pull/41898) | Update dependencies |
| 0.2.3 | 2024-07-10 | [41525](https://github.com/airbytehq/airbyte/pull/41525) | Update dependencies |
| 0.2.2 | 2024-07-09 | [41232](https://github.com/airbytehq/airbyte/pull/41232) | Update dependencies |
| 0.2.1 | 2024-07-06 | [40791](https://github.com/airbytehq/airbyte/pull/40791) | Update dependencies |
| 0.2.0 | 2024-06-27 | [40216](https://github.com/airbytehq/airbyte/pull/40216) | Migrate connector to Low Code |
| 0.1.9 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.8 | 2024-06-25 | [40324](https://github.com/airbytehq/airbyte/pull/40324) | Update dependencies |
| 0.1.7 | 2024-06-22 | [40145](https://github.com/airbytehq/airbyte/pull/40145) | Update dependencies |
| 0.1.6 | 2024-06-06 | [39228](https://github.com/airbytehq/airbyte/pull/39228) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.5 | 2024-06-03 | [38916](https://github.com/airbytehq/airbyte/pull/38916) | Replace AirbyteLogger with logging.Logger |
| 0.1.4 | 2024-06-03 | [38916](https://github.com/airbytehq/airbyte/pull/38916) | Replace AirbyteLogger with logging.Logger |
| 0.1.3 | 2024-05-20 | [38372](https://github.com/airbytehq/airbyte/pull/38372) | [autopull] base image + poetry + up_to_date |
| 0.1.2   | 2022-07-06 | [28009](https://github.com/airbytehq/airbyte/pull/28009/) | Migrated to advancedOAuth        |
| 0.1.1   | 2022-11-01 | [18826](https://github.com/airbytehq/airbyte/pull/18826)  | Fix stream analytics_conversions |
| 0.1.0   | 2022-10-23 | [18348](https://github.com/airbytehq/airbyte/pull/18348)  | Initial Release                  |

</details>
