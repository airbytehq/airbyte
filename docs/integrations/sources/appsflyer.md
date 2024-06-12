# AppsFlyer

The Airbyte Source for [AppsFLyer](https://www.appsflyer.com/)

## Supported Streams

| Category                     | Status                |
|------------------------------|-----------------------|
| Raw Data (Non-Organic)       | ✔️ (Except Reinstall) |
| Raw Data (Organic)           | ✔️ (Except Reinstall) |
| Raw Data (Retargeting)       | ✔️                    |
| Ad Revenue                   | ❌                     |
| Postback                     | ❌                     |
| Protect360 Fraud             | ❌                     |
| Aggregate Report             | ✔️                    |
| Aggregate Retargeting Report | ✔️                    |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                                     |
| :------ | :--------- | :----------------------------------------------------- | :------------------------------------------ |
| 0.2.1   | 2024-06-11 | [39407](https://github.com/airbytehq/airbyte/pull/39407) | Fix Organic In-App Events Stream |
| 0.2.0   | 2024-05-19 | [38339](https://github.com/airbytehq/airbyte/pull/38339) | Migrate to [AppyFlyer API V2](https://support.appsflyer.com/hc/en-us/articles/12399683708305-Bulletin-API-token-changes?query=token)             |
| 0.1.2 | 2024-06-06 | [39187](https://github.com/airbytehq/airbyte/pull/39187) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38436](https://github.com/airbytehq/airbyte/pull/38436) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2021-03-22 | [2544](https://github.com/airbytehq/airbyte/pull/2544) | Adding the appsflyer singer based connector |

</details>
