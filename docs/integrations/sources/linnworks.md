# Linnworks

## Sync overview

Linnworks source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python). Airbyte uses [Linnworks API](https://apps.linnworks.net/Api) to fetch data from Linnworks.

### Output schema

This Source is capable of syncing the following data as streams:

- [StockLocations](https://apps.linnworks.net/Api/Method/Inventory-GetStockLocations)
- [StockLocationDetails](https://apps.linnworks.net/Api/Method/Locations-GetLocation)
- [StockItems](https://apps.linnworks.net//Api/Method/Stock-GetStockItemsFull)
- [ProcessedOrders](https://apps.linnworks.net/Api/Method/ProcessedOrders-SearchProcessedOrders)
- [ProcessedOrderDetails](https://apps.linnworks.net/Api/Method/Orders-GetOrdersById)

### Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `date`           | `string`     | FORMAT YYYY-MM-DD          |
| `datetime`       | `string`     | FORMAT YYYY-MM-DDThh:mm:ss |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |

### Features

| Feature                                   | Supported?\(Yes/No\) | Notes |
| :---------------------------------------- | :------------------- | :---- |
| Full Refresh Overwrite Sync               | Yes                  |       |
| Full Refresh Append Sync                  | Yes                  |       |
| Incremental - Append Sync                 | Yes                  |       |
| Incremental - Append + Deduplication Sync | Yes                  |       |
| Namespaces                                | No                   |       |

### Performance considerations

Rate limit varies across Linnworks API endpoint. See the endpoint documentation to learn more. Rate limited requests will receive a 429 response. The Linnworks connector should not run into Linnworks API limitations under normal usage.

## Getting started

### Authentication

Linnworks platform has two portals: seller and developer. First, to create API credentials, log in to the [developer portal](https://developer.linnworks.com) and create an application of type `System Integration`. Then click on provided Installation URL and proceed with an installation wizard. The wizard will show a token that you will need for authentication. The installed application will be present on your account on [seller portal](https://login.linnworks.net/).

Authentication credentials can be obtained on developer portal section Applications -> _Your application name_ -> Edit -> General. And the token, if you missed it during the install, can be obtained anytime under the section Applications -> _Your application name_ -> Installs.

## Changelog

| Version | Date       | Pull Request                                           | Subject                                                                     |
| :------ | :--------- | :----------------------------------------------------- | :-------------------------------------------------------------------------- |
| 0.1.5   | Unknown    | Unknown                                                | Bump Version                                                                |
| 0.1.4   | 2021-11-24 | [8226](https://github.com/airbytehq/airbyte/pull/8226) | Source Linnworks: improve streams ProcessedOrders and ProcessedOrderDetails |
| 0.1.3   | 2021-11-24 | [8169](https://github.com/airbytehq/airbyte/pull/8169) | Source Linnworks: refactor stream StockLocations                            |
| 0.1.2   | 2021-11-23 | [8177](https://github.com/airbytehq/airbyte/pull/8177) | Source Linnworks: add stream ProcessedOrderDetails                          |
| 0.1.0   | 2021-11-09 | [7588](https://github.com/airbytehq/airbyte/pull/7588) | New Source: Linnworks                                                       |
