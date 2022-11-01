# Microsoft Dataverse

## Sync overview

This source can sync data for the [Microsoft Dataverse API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview) to work with [Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/overview).

This connector currently uses version v9.2 of the API

### Output schema

This source will automatically discover the schema of the Entities of your Dataverse instance using the API
https://<url>/api/data/v9.2/EntityDefinitions?$expand=Attributes

### Data type mapping

| Integration Type | Airbyte Type              | Notes                 |
|:-----------------|:--------------------------|:----------------------|
| `String`         | `string`                  |                       |
| `DateTime`       | `timestamp with timezone` |                       |
| `Integer`        | `integer`                 |                       |
| `Money`          | `number`                  |                       |
| `Boolean`        | `boolean`                 |                       |
| `Double`         | `number`                  |                       |
| `Decimal`        | `number`                  |                       |
| `Virtual`        | None                      | We skip virtual types |

### Features

| Feature                       | Supported?\(Yes/No\) | Notes                                                      |
|:------------------------------|:---------------------|:-----------------------------------------------------------|
| Full Refresh Sync             | Yes                  |                                                            |
| Incremental Sync              | Yes                  |                                                            |
| CDC                           | Yes                  | Not all entities support it. Deleted data only have the ID |
| Replicate Incremental Deletes | Yes                  |                                                            |
| SSL connection                | Yes                  |                                                            |
| Namespaces                    | No                   |                                                            |

## Getting started

### Requirements

* Application \(client\) ID
* Directory \(tenant\) ID
* Client secrets

### Setup guide

The Microsoft Dataverse API uses OAuth2 for authentication. We need a 'client_credentials' type, that usually
we get by using an App Registration.

https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth

## CHANGELOG

| Version | Date | Pull Request | Subject |
|:--------|:-----|:-------------|:--------|
