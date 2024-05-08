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

## CHANGELOG

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| 0.1.2   | 2023-08-24 | [29732](https://github.com/airbytehq/airbyte/pull/29732) | 🐛 Source Microsoft Dataverse: Adjust source_default_cursor when modifiedon not exists |
| 0.1.1   | 2023-03-16 | [22805](https://github.com/airbytehq/airbyte/pull/22805) | Fixed deduped cursor field value update                                                |
| 0.1.0   | 2022-11-14 | [18646](https://github.com/airbytehq/airbyte/pull/18646) | 🎉 New Source: Microsoft Dataverse [python cdk]                                        |
