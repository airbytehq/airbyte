# Microsoft Dataverse

## Sync overview

This source can sync data for the [Microsoft Dataverse API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview) to work with [Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/overview).

This connector currently uses version v9.2 of the API

### Output schema

This source will automatically discover the schema of the Entities of your Dataverse instance using the API
`https://<url>/api/data/v9.2/EntityDefinitions?$expand=Attributes`

### Data type mapping

| Integration Type   | Airbyte Type              | Notes                 |
| :----------------- | :------------------------ | :-------------------- |
| `String`           | `string`                  |                       |
| `UniqueIdentifier` | `string`                  |                       |
| `DateTime`         | `timestamp with timezone` |                       |
| `Integer`          | `integer`                 |                       |
| `BigInt`           | `integer`                 |                       |
| `Money`            | `number`                  |                       |
| `Boolean`          | `boolean`                 |                       |
| `Double`           | `number`                  |                       |
| `Decimal`          | `number`                  |                       |
| `Status`           | `integer`                 |                       |
| `State`            | `integer`                 |                       |
| `Virtual`          | None                      | We skip virtual types |

Other types are defined as `string`.

### Features

| Feature                       | Supported?\(Yes/No\) | Notes                                                      |
| :---------------------------- | :------------------- | :--------------------------------------------------------- |
| Full Refresh Sync             | Yes                  |                                                            |
| Incremental Sync              | Yes                  |                                                            |
| CDC                           | Yes                  | Not all entities support it. Deleted data only have the ID |
| Replicate Incremental Deletes | Yes                  |                                                            |
| SSL connection                | Yes                  |                                                            |
| Namespaces                    | No                   |                                                            |

## Getting started

### Requirements

- Application \(client\) ID
- Directory \(tenant\) ID
- Client secrets

### Setup guide

The Microsoft Dataverse API uses OAuth2 for authentication. We need a 'client_credentials' type, that we usually get by using an App Registration.
https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth

The procedure to generate the credentials and setup the necessary permissions is well described in this post from Magnetism blog:
https://blog.magnetismsolutions.com/blog/paulnieuwelaar/2021/9/21/setting-up-an-application-user-in-dynamics-365

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| 0.1.21 | 2024-09-26 | [ ](https://github.com/airbytehq/airbyte/pull/ ) | Make Dataverse available on Airbyte Cloud |
| 0.1.20 | 2024-09-21 | [45777](https://github.com/airbytehq/airbyte/pull/45777) | Update dependencies |
| 0.1.19 | 2024-09-14 | [45482](https://github.com/airbytehq/airbyte/pull/45482) | Update dependencies |
| 0.1.18 | 2024-09-07 | [45224](https://github.com/airbytehq/airbyte/pull/45224) | Update dependencies |
| 0.1.17 | 2024-08-31 | [44987](https://github.com/airbytehq/airbyte/pull/44987) | Update dependencies |
| 0.1.16 | 2024-08-24 | [44640](https://github.com/airbytehq/airbyte/pull/44640) | Update dependencies |
| 0.1.15 | 2024-08-17 | [44224](https://github.com/airbytehq/airbyte/pull/44224) | Update dependencies |
| 0.1.14 | 2024-08-10 | [43653](https://github.com/airbytehq/airbyte/pull/43653) | Update dependencies |
| 0.1.13 | 2024-08-03 | [43164](https://github.com/airbytehq/airbyte/pull/43164) | Update dependencies |
| 0.1.12 | 2024-07-27 | [42612](https://github.com/airbytehq/airbyte/pull/42612) | Update dependencies |
| 0.1.11 | 2024-07-20 | [42373](https://github.com/airbytehq/airbyte/pull/42373) | Update dependencies |
| 0.1.10 | 2024-07-13 | [41920](https://github.com/airbytehq/airbyte/pull/41920) | Update dependencies |
| 0.1.9 | 2024-07-10 | [41346](https://github.com/airbytehq/airbyte/pull/41346) | Update dependencies |
| 0.1.8 | 2024-07-09 | [41247](https://github.com/airbytehq/airbyte/pull/41247) | Update dependencies |
| 0.1.7 | 2024-07-06 | [40800](https://github.com/airbytehq/airbyte/pull/40800) | Update dependencies |
| 0.1.6 | 2024-06-25 | [40340](https://github.com/airbytehq/airbyte/pull/40340) | Update dependencies |
| 0.1.5 | 2024-06-21 | [39931](https://github.com/airbytehq/airbyte/pull/39931) | Update dependencies |
| 0.1.4 | 2024-06-06 | [39265](https://github.com/airbytehq/airbyte/pull/39265) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.3 | 2024-05-20 | [38397](https://github.com/airbytehq/airbyte/pull/38397) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-08-24 | [29732](https://github.com/airbytehq/airbyte/pull/29732) | 🐛 Source Microsoft Dataverse: Adjust source_default_cursor when modifiedon not exists |
| 0.1.1 | 2023-03-16 | [22805](https://github.com/airbytehq/airbyte/pull/22805) | Fixed deduped cursor field value update |
| 0.1.0 | 2022-11-14 | [18646](https://github.com/airbytehq/airbyte/pull/18646) | 🎉 New Source: Microsoft Dataverse [python cdk] |

</details>
