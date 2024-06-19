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
| 0.1.3   | 2024-06-17 | [38661](https://github.com/airbytehq/airbyte/pull/38661) | Make connector compatible with Builder |
| 0.1.2   | 2024-06-04 | [39012](https://github.com/airbytehq/airbyte/pull/39012) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1   | 2024-05-20 | [38409](https://github.com/airbytehq/airbyte/pull/38409) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-22 | [18844](https://github.com/airbytehq/airbyte/pull/18844) | Add Reply.io Source Connector |

</details>