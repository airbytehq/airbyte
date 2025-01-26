# Reply.io

## Sync overview

The Reply.io source supports both Full Refresh only.

This source can sync data for the [Reply.io API](https://apidocs.reply.io/#intro).

### Output schema

This Source is capable of syncing the following core Streams:

- [blacklist](https://apidocs.reply.io/#9251a79b-3d16-478c-acfd-dfe1eb49e85a)
- [campaigns](https://apidocs.reply.io/#4c035861-5dc9-4ba2-8adf-24e55c83e5f0)
- [email_accounts](https://apidocs.reply.io/#2f59ac90-fe00-440c-a841-3bd11ce8f28f)
- [people](https://apidocs.reply.io/#0a39db6f-af24-494f-88d6-caefd76b40f9)
- [templates](https://apidocs.reply.io/#5e4650a6-f2d7-4a9f-86ed-ca863360fcca)

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | No                   |       |
| Namespaces                | No                   |       |

### Performance considerations

- Each Reply user has a limit of 15000 API calls per month.
- The time limit between API calls makes 10 seconds.
- The limit for syncing contacts using native integrations is the same as the limit for the number of contacts in your Reply account.

## Requirements

- **Reply.io API key**. See the [Reply.io docs](https://apidocs.reply.io/#authentication) for information on how to obtain an API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                       |
|:--------|:-----------| :------------------------------------------------------- | :---------------------------- |
| 0.2.9 | 2025-01-25 | [52537](https://github.com/airbytehq/airbyte/pull/52537) | Update dependencies |
| 0.2.8 | 2025-01-18 | [51876](https://github.com/airbytehq/airbyte/pull/51876) | Update dependencies |
| 0.2.7 | 2025-01-11 | [51337](https://github.com/airbytehq/airbyte/pull/51337) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50720](https://github.com/airbytehq/airbyte/pull/50720) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50229](https://github.com/airbytehq/airbyte/pull/50229) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49664](https://github.com/airbytehq/airbyte/pull/49664) | Update dependencies |
| 0.2.3 | 2024-12-12 | [48261](https://github.com/airbytehq/airbyte/pull/48261) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47872](https://github.com/airbytehq/airbyte/pull/47872) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47462](https://github.com/airbytehq/airbyte/pull/47462) | Update dependencies |
| 0.2.0 | 2024-08-19 | [44407](https://github.com/airbytehq/airbyte/pull/44407) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-17 | [44284](https://github.com/airbytehq/airbyte/pull/44284) | Update dependencies |
| 0.1.14 | 2024-08-12 | [43818](https://github.com/airbytehq/airbyte/pull/43818) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43696](https://github.com/airbytehq/airbyte/pull/43696) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43215](https://github.com/airbytehq/airbyte/pull/43215) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42827](https://github.com/airbytehq/airbyte/pull/42827) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42246](https://github.com/airbytehq/airbyte/pull/42246) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41737](https://github.com/airbytehq/airbyte/pull/41737) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41497](https://github.com/airbytehq/airbyte/pull/41497) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41302](https://github.com/airbytehq/airbyte/pull/41302) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40805](https://github.com/airbytehq/airbyte/pull/40805) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40283](https://github.com/airbytehq/airbyte/pull/40283) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40137](https://github.com/airbytehq/airbyte/pull/40137) | Update dependencies |
| 0.1.3 | 2024-06-17 | [38661](https://github.com/airbytehq/airbyte/pull/38661) | Make connector compatible with Builder |
| 0.1.2 | 2024-06-04 | [39012](https://github.com/airbytehq/airbyte/pull/39012) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-20 | [38409](https://github.com/airbytehq/airbyte/pull/38409) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-22 | [18844](https://github.com/airbytehq/airbyte/pull/18844) | Add Reply.io Source Connector |

</details>
