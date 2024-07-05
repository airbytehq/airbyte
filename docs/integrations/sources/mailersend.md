# Mailersend

## Sync overview

This source can sync data from the [Mailersend](https://developers.mailersend.com/#mailersend-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch.

## This Source Supports the Following Streams

- [activity](https://developers.mailersend.com/api/v1/activity.html#get-a-list-of-activities)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

MailerSend has a default [rate limit](https://developers.mailersend.com/general.html#api-response) of 60 requests per minute on general API endpoints.

## Getting started

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                  |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------- |
| 0.1.2 | 2024-06-06 | [39237](https://github.com/airbytehq/airbyte/pull/39237) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-31 | [38811](https://github.com/airbytehq/airbyte/pull/38811) | [autopull] Migrate to base image and poetry |
| 0.1.0 | 2022-11-13 | [18669](https://github.com/airbytehq/airbyte/pull/18669) | 🎉 New Source: Mailersend [low-code CDK] |

</details>
