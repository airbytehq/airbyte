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
| 0.2.9 | 2025-01-11 | [51156](https://github.com/airbytehq/airbyte/pull/51156) | Update dependencies |
| 0.2.8 | 2024-12-28 | [50650](https://github.com/airbytehq/airbyte/pull/50650) | Update dependencies |
| 0.2.7 | 2024-12-21 | [50080](https://github.com/airbytehq/airbyte/pull/50080) | Update dependencies |
| 0.2.6 | 2024-12-14 | [49614](https://github.com/airbytehq/airbyte/pull/49614) | Update dependencies |
| 0.2.5 | 2024-12-12 | [49262](https://github.com/airbytehq/airbyte/pull/49262) | Update dependencies |
| 0.2.4 | 2024-12-11 | [48947](https://github.com/airbytehq/airbyte/pull/48947) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.3 | 2024-11-04 | [48203](https://github.com/airbytehq/airbyte/pull/48203) | Update dependencies |
| 0.2.2 | 2024-10-29 | [47785](https://github.com/airbytehq/airbyte/pull/47785) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47592](https://github.com/airbytehq/airbyte/pull/47592) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44766](https://github.com/airbytehq/airbyte/pull/44766) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-24 | [44697](https://github.com/airbytehq/airbyte/pull/44697) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44258](https://github.com/airbytehq/airbyte/pull/44258) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43928](https://github.com/airbytehq/airbyte/pull/43928) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43564](https://github.com/airbytehq/airbyte/pull/43564) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43086](https://github.com/airbytehq/airbyte/pull/43086) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42700](https://github.com/airbytehq/airbyte/pull/42700) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42273](https://github.com/airbytehq/airbyte/pull/42273) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41696](https://github.com/airbytehq/airbyte/pull/41696) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41557](https://github.com/airbytehq/airbyte/pull/41557) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41322](https://github.com/airbytehq/airbyte/pull/41322) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40856](https://github.com/airbytehq/airbyte/pull/40856) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40473](https://github.com/airbytehq/airbyte/pull/40473) | Update dependencies |
| 0.1.3 | 2024-06-22 | [39995](https://github.com/airbytehq/airbyte/pull/39995) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39237](https://github.com/airbytehq/airbyte/pull/39237) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-31 | [38811](https://github.com/airbytehq/airbyte/pull/38811) | [autopull] Migrate to base image and poetry |
| 0.1.0 | 2022-11-13 | [18669](https://github.com/airbytehq/airbyte/pull/18669) | 🎉 New Source: Mailersend [low-code CDK] |

</details>
