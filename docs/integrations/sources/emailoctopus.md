# EmailOctopus

## Requirements
* [EmailOctopus account](https://help.emailoctopus.com)
* EmailOctopus [API key](https://help.emailoctopus.com/article/165-how-to-create-and-delete-api-keys)

## Supported sync modes

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes | [Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) |
| Incremental Sync | No |  |

## Supported Streams

* [Get all campaigns](https://emailoctopus.com/api-documentation/campaigns/get-all)
* [Get all lists](https://emailoctopus.com/api-documentation/lists/get-all)

## Performance considerations

No documented strict rate limit.

## Changelog

| Version | Date       | Pull Request | Subject                                                    |
|:--------|:-----------| :----------- |:-----------------------------------------------------------|
| 0.1.0   | 2022-10-29 | [18647](https://github.com/airbytehq/airbyte/pull/18647) | Initial commit |