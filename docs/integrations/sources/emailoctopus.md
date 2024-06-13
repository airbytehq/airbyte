# EmailOctopus

## Requirements

- [EmailOctopus account](https://help.emailoctopus.com)
- EmailOctopus [API key](https://help.emailoctopus.com/article/165-how-to-create-and-delete-api-keys)

## Supported sync modes

| Feature           | Supported?\(Yes/No\) | Notes                                                                                          |
| :---------------- | :------------------- | :--------------------------------------------------------------------------------------------- |
| Full Refresh Sync | Yes                  | [Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) |
| Incremental Sync  | No                   |                                                                                                |

## Supported Streams

- [Get all campaigns](https://emailoctopus.com/api-documentation/campaigns/get-all)
- [Get all lists](https://emailoctopus.com/api-documentation/lists/get-all)

## Performance considerations

No documented strict rate limit.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.5 | 2024-06-04 | [38945](https://github.com/airbytehq/airbyte/pull/38945) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.4 | 2024-05-28 | [38718](https://github.com/airbytehq/airbyte/pull/38718) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.3 | 2024-04-19 | [37154](https://github.com/airbytehq/airbyte/pull/37154) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37154](https://github.com/airbytehq/airbyte/pull/37154) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37154](https://github.com/airbytehq/airbyte/pull/37154) | schema descriptions |
| 0.1.0 | 2022-10-29 | [18647](https://github.com/airbytehq/airbyte/pull/18647) | Initial commit |

</details>
